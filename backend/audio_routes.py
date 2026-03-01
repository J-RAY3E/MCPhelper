"""
Audio API Routes for MCPDESK Backend
Endpoints for speech-to-text (Whisper) and text-to-speech (TTS)
"""

import os
import tempfile
from typing import Optional
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/audio", tags=["audio"])

# Audio processors (lazy loaded)
_whisper_processor = None
_tts_processor = None
_audio_recorder = None


def get_whisper_processor():
    """Get or create Whisper processor"""
    global _whisper_processor
    if _whisper_processor is None:
        try:
            from backend.audio.whisper_processor import WhisperProcessor
            _whisper_processor = WhisperProcessor(model_name="base")
        except Exception as e:
            print(f"Error loading Whisper: {e}")
            return None
    return _whisper_processor


def get_tts_processor():
    """Get or create TTS processor"""
    global _tts_processor
    if _tts_processor is None:
        try:
            from backend.audio.tts_processor import TTSProcessor
            _tts_processor = TTSProcessor()
        except Exception as e:
            print(f"Error loading TTS: {e}")
            return None
    return _tts_processor


# ── Request Models ────────────────────────────────────────────────────────────

class TTSRequest(BaseModel):
    text: str
    voice: Optional[str] = None
    rate: Optional[int] = 150
    volume: Optional[float] = 1.0


class TranscriptionRequest(BaseModel):
    language: Optional[str] = "auto"
    model: Optional[str] = "base"


# ── Endpoints ────────────────────────────────────────────────────────────────

@router.post("/transcribe")
async def transcribe_audio(
    audio: UploadFile = File(...),
    language: str = "auto",
    model: str = "base"
):
    """
    Transcribe audio file to text using Whisper.
    
    Args:
        audio: Audio file (wav, mp3, ogg, flac)
        language: Language code or "auto" for detection
        model: Whisper model size
    
    Returns:
        Transcription result with text and metadata
    """
    # Validate file
    allowed_extensions = ['.wav', '.mp3', '.ogg', '.flac', '.m4a', '.webm']
    file_ext = os.path.splitext(audio.filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format. Allowed: {', '.join(allowed_extensions)}"
        )
    
    # Save uploaded file
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp:
        content = await audio.read()
        tmp.write(content)
        tmp_path = tmp.name
    
    try:
        # Get processor
        processor = get_whisper_processor()
        if processor is None:
            raise HTTPException(
                status_code=500,
                detail="Whisper not available. Install: pip install openai-whisper"
            )
        
        # Transcribe
        result = processor.transcribe_audio(tmp_path, language=language)
        
        if result.get("success"):
            return {
                "success": True,
                "text": result["text"],
                "language": result.get("language", language),
                "duration": result.get("duration", 0),
                "segments": result.get("segments", [])
            }
        else:
            raise HTTPException(
                status_code=500,
                detail=result.get("error", "Transcription failed")
            )
    
    finally:
        # Cleanup
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


@router.post("/speak")
async def text_to_speech(request: TTSRequest):
    """
    Convert text to speech using pyttsx3.
    
    Args:
        request: TTS request with text and options
    
    Returns:
        Audio file path or streaming audio
    """
    if not request.text:
        raise HTTPException(status_code=400, detail="Text is required")
    
    # Get processor
    processor = get_tts_processor()
    if processor is None:
        raise HTTPException(
            status_code=500,
            detail="TTS not available. Install: pip install pyttsx3"
        )
    
    try:
        # Configure TTS
        if request.rate:
            processor.set_rate(request.rate)
        if request.volume:
            processor.set_volume(request.volume)
        if request.voice:
            processor.set_voice(request.voice)
        
        # Generate speech to file
        result = processor.save_to_file(request.text)
        
        if result.get("success"):
            return {
                "success": True,
                "audio_file": result["audio_file"],
                "duration": result.get("duration", 0)
            }
        else:
            raise HTTPException(
                status_code=500,
                detail=result.get("error", "TTS failed")
            )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/voices")
async def get_available_voices():
    """
    Get list of available TTS voices.
    
    Returns:
        List of available voices
    """
    processor = get_tts_processor()
    if processor is None:
        return {"voices": [], "error": "TTS not available"}
    
    try:
        voices = processor.get_voices()
        return {"voices": voices}
    except Exception as e:
        return {"voices": [], "error": str(e)}


@router.get("/models")
async def get_whisper_models():
    """
    Get list of available Whisper models.
    
    Returns:
        List of available models
    """
    processor = get_whisper_processor()
    if processor is None:
        return {"models": [], "error": "Whisper not available"}
    
    return {
        "models": processor.get_available_models(),
        "current": processor.model_name
    }


@router.get("/status")
async def audio_status():
    """
    Get audio system status.
    
    Returns:
        Status of STT and TTS systems
    """
    whisper_ok = get_whisper_processor() is not None and get_whisper_processor().is_loaded()
    tts_ok = get_tts_processor() is not None and get_tts_processor().is_available()
    
    return {
        "stt_available": whisper_ok,
        "tts_available": tts_ok,
        "stt_model": get_whisper_processor().model_name if whisper_ok else None,
        "platform": os.name
    }
