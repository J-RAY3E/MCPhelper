import asyncio
import base64
import tempfile
import os
import requests
from nicegui import ui
from ..config.settings import BACKEND_URL
from ..state.store import cells, voice_status

def start_voice():
    js_code = '''
    if (!window.voiceAssistant) {
        window.voiceAssistant = { mediaRecorder: null, audioChunks: [], stream: null, isRecording: false };
    }
    if (window.voiceAssistant.isRecording) { return; }
    navigator.mediaDevices.getUserMedia({ audio: true })
        .then(stream => {
            window.voiceAssistant.stream = stream;
            window.voiceAssistant.audioChunks = [];
            window.voiceAssistant.mediaRecorder = new MediaRecorder(stream);
            window.voiceAssistant.isRecording = true;
            window.voiceAssistant.mediaRecorder.ondataavailable = event => {
                window.voiceAssistant.audioChunks.push(event.data);
            };
            window.voiceAssistant.mediaRecorder.onstop = () => {
                window.voiceAssistant.isRecording = false;
                const audioBlob = new Blob(window.voiceAssistant.audioChunks, { type: 'audio/wav' });
                const reader = new FileReader();
                reader.onload = function() {
                    window.voiceAudioData = reader.result;
                    window.voiceRecordingDone = true;
                };
                reader.readAsDataURL(audioBlob);
                if (window.voiceAssistant.stream) {
                    window.voiceAssistant.stream.getTracks().forEach(track => track.stop());
                }
            };
            window.voiceAssistant.mediaRecorder.start();
            if (window.voiceStatusEl) window.voiceStatusEl.textContent = '🎤 Grabando...';
        })
        .catch(err => {
            console.error("Mic error:", err);
            alert("Error accessing microphone: " + err.message);
            window.voiceAssistant.isRecording = false;
        });
    '''
    ui.run_javascript(js_code, respond=False)
    if voice_status:
        voice_status.set_text('🎤 Grabando...')

def stop_voice():
    js_code = '''
    if (window.voiceAssistant && window.voiceAssistant.mediaRecorder && window.voiceAssistant.isRecording) {
        window.voiceAssistant.mediaRecorder.stop();
        if (window.voiceStatusEl) window.voiceStatusEl.textContent = '⏳ Procesando...';
    }
    '''
    ui.run_javascript(js_code, respond=False)
    
    async def process_voice():
        await asyncio.sleep(2)
        await check_and_send_voice()
    
    asyncio.create_task(process_voice())

async def check_and_send_voice():
    js_check = '''
    if (window.voiceRecordingDone && window.voiceAudioData) {
        window.voiceRecordingDone = false;
        window.voiceAudioData;
    } else { null; }
    '''
    result = ui.run_javascript(js_check)
    
    if not result:
        if voice_status:
            voice_status.set_text('🎤 Escuchar')
        return
    
    try:
        audio_data = result.split(',')[1] if ',' in result else result
        audio_bytes = base64.b64decode(audio_data)
        
        temp_dir = tempfile.gettempdir()
        filepath = os.path.join(temp_dir, "voice_input.wav")
        
        with open(filepath, 'wb') as f:
            f.write(audio_bytes)
        
        if voice_status:
            voice_status.set_text('⏳ Transcribiendo...')
        
        with open(filepath, 'rb') as f:
            files = {'audio': f}
            resp = requests.post(f"{BACKEND_URL}/audio/transcribe", files=files, timeout=120)
        
        os.unlink(filepath)
        
        if resp.status_code == 200:
            result_data = resp.json()
            if result_data.get("success"):
                transcription = result_data.get("text", "").strip()
                
                if voice_status:
                    voice_status.set_text('⏳ Enviando...')
                
                cmd_resp = requests.post(
                    f"{BACKEND_URL}/command",
                    json={"command": transcription},
                    timeout=120
                )
                
                from ..state.store import Cell
                from ..components.cell import render_cells
                
                new_cell = Cell()
                new_cell.content = transcription
                new_cell.result = cmd_resp.json() if cmd_resp.status_code == 200 else {"type": "error", "content": cmd_resp.text}
                cells.append(new_cell)
                render_cells()
                
                if voice_status:
                    voice_status.set_text('🎤 Escuchar')
                
                ui.notify("Comando enviado", type="positive", position="top-right")
                return
        
        if voice_status:
            voice_status.set_text('❌ Error')
        ui.notify("Error en transcripción", type="negative", position="top-right")
        
    except Exception as e:
        if voice_status:
            voice_status.set_text('❌ Error')
        ui.notify(f"Error: {str(e)}", type="negative", position="top-right")

def toggle_voice():
    js_check = 'window.voiceAssistant && window.voiceAssistant.isRecording;'
    is_recording = ui.run_javascript(js_check)
    
    if is_recording:
        stop_voice()
    else:
        start_voice()
