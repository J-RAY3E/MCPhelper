"""
Audio Recorder - Capture audio from microphone
100% offline recording using various backends
"""

import os
import tempfile
import platform
from typing import Optional, Dict, Any, List
from pathlib import Path


class AudioRecorder:
    """
    Cross-platform audio recorder for capturing microphone input.
    Supports multiple backends: pyaudio, sounddevice, or JavaScript (browser).
    """
    
    def __init__(self, sample_rate: int = 16000, channels: int = 1, 
                 chunk_size: int = 1024, backend: str = "auto"):
        """
        Initialize audio recorder.
        
        Args:
            sample_rate: Audio sample rate (default 16000 for speech)
            channels: Number of audio channels (1 = mono)
            chunk_size: Buffer size for recording
            backend: Backend to use - 'pyaudio', 'sounddevice', 'javascript', or 'auto'
        """
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = chunk_size
        self.backend = backend
        self.recording = False
        self.frames = []
        self.stream = None
        self._audio = None
        self._select_backend()
    
    def _select_backend(self):
        """Select available audio backend"""
        if self.backend == "auto":
            # Try to find best available backend
            try:
                import sounddevice
                self.backend = "sounddevice"
            except ImportError:
                try:
                    import pyaudio
                    self.backend = "pyaudio"
                except ImportError:
                    self.backend = "javascript"
        
        print(f"Using audio backend: {self.backend}")
    
    def start_recording(self) -> Dict[str, Any]:
        """
        Start recording audio.
        
        Returns:
            Dictionary with start status
        """
        if self.recording:
            return {
                "success": False,
                "error": "Already recording"
            }
        
        try:
            self.frames = []
            
            if self.backend == "sounddevice":
                return self._start_sounddevice()
            elif self.backend == "pyaudio":
                return self._start_pyaudio()
            elif self.backend == "javascript":
                return {
                    "success": True,
                    "message": "JavaScript recording initiated - use browser microphone"
                }
            else:
                return {
                    "success": False,
                    "error": f"Unsupported backend: {self.backend}"
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error starting recording: {str(e)}"
            }
    
    def _start_sounddevice(self) -> Dict[str, Any]:
        """Start recording using sounddevice"""
        try:
            import sounddevice as sd
            import numpy as np
            
            self._audio = sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                blocksize=self.chunk_size,
                callback=self._sounddevice_callback
            )
            self._audio.start()
            self.recording = True
            
            return {
                "success": True,
                "message": "Recording started with sounddevice"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"sounddevice error: {str(e)}"
            }
    
    def _sounddevice_callback(self, indata, frames, time, status):
        """Callback for sounddevice streaming"""
        if self.recording:
            self.frames.append(indata.copy())
    
    def _start_pyaudio(self) -> Dict[str, Any]:
        """Start recording using pyaudio"""
        try:
            import pyaudio
            
            self._audio = pyaudio.PyAudio()
            self.stream = self._audio.open(
                format=pyaudio.paInt16,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size,
                stream_callback=self._pyaudio_callback
            )
            self.stream.start_stream()
            self.recording = True
            
            return {
                "success": True,
                "message": "Recording started with pyaudio"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"pyaudio error: {str(e)}"
            }
    
    def _pyaudio_callback(self, in_data, frame_count, time_info, status):
        """Callback for pyaudio streaming"""
        if self.recording:
            self.frames.append(in_data)
        return (in_data, pyaudio.paContinue)
    
    def stop_recording(self, filename: Optional[str] = None) -> Dict[str, Any]:
        """
        Stop recording and optionally save to file.
        
        Args:
            filename: Optional output file path
            
        Returns:
            Dictionary with recording data or file path
        """
        if not self.recording:
            return {
                "success": False,
                "error": "Not recording"
            }
        
        try:
            self.recording = False
            
            # Stop audio streams
            if self.backend == "sounddevice" and self._audio:
                self._audio.stop()
                self._audio.close()
            elif self.backend == "pyaudio" and self.stream:
                self.stream.stop_stream()
                self.stream.close()
                if self._audio:
                    self._audio.terminate()
            
            # Process recorded audio
            audio_data = self._process_frames()
            
            if filename:
                return self._save_to_file(audio_data, filename)
            
            return {
                "success": True,
                "audio_data": audio_data,
                "duration": len(audio_data) / self.sample_rate if len(audio_data) > 0 else 0
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error stopping recording: {str(e)}"
            }
    
    def _process_frames(self):
        """Process recorded frames into audio array"""
        try:
            import numpy as np
            
            if self.backend == "sounddevice":
                import numpy as np
                return np.concatenate(self.frames) if self.frames else np.array([])
            elif self.backend == "pyaudio":
                import wave
                import io
                
                # Combine frames
                audio_bytes = b''.join(self.frames)
                
                # Convert to numpy array
                audio_array = np.frombuffer(audio_bytes, dtype=np.int16)
                return audio_array.astype(np.float32) / 32768.0
            else:
                return b''.join(self.frames)
        except Exception as e:
            print(f"Error processing frames: {e}")
            return b''
    
    def _save_to_file(self, audio_data, filename: str) -> Dict[str, Any]:
        """Save audio data to file"""
        try:
            import numpy as np
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            if self.backend == "sounddevice":
                import soundfile as sf
                sf.write(filename, audio_data, self.sample_rate)
            elif self.backend == "pyaudio":
                import wave
                
                with wave.open(filename, 'wb') as wf:
                    wf.setnchannels(self.channels)
                    wf.setsampwidth(2)  # 16-bit
                    wf.setframerate(self.sample_rate)
                    wf.writeframes(audio_data.tobytes())
            else:
                with open(filename, 'wb') as f:
                    f.write(audio_data)
            
            return {
                "success": True,
                "filename": filename,
                "duration": len(audio_data) / self.sample_rate if hasattr(audio_data, '__len__') else 0
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error saving file: {str(e)}"
            }
    
    def get_devices(self) -> List[Dict[str, Any]]:
        """
        Get list of available audio input devices.
        
        Returns:
            List of device dictionaries
        """
        devices = []
        
        try:
            if self.backend == "sounddevice":
                import sounddevice as sd
                for i, dev in enumerate(sd.query_devices()):
                    if dev['max_input_channels'] > 0:
                        devices.append({
                            "index": i,
                            "name": dev['name'],
                            "channels": dev['max_input_channels'],
                            "sample_rate": dev['default_samplerate']
                        })
            elif self.backend == "pyaudio":
                import pyaudio
                p = pyaudio.PyAudio()
                for i in range(p.get_device_count()):
                    info = p.get_device_info_by_index(i)
                    if info['maxInputChannels'] > 0:
                        devices.append({
                            "index": i,
                            "name": info['name'],
                            "channels": info['maxInputChannels'],
                            "sample_rate": info['defaultSampleRate']
                        })
                p.terminate()
        except Exception as e:
            print(f"Error getting devices: {e}")
        
        return devices
    
    def is_recording(self) -> bool:
        """Check if currently recording"""
        return self.recording
    
    def is_available(self) -> bool:
        """Check if audio recording is available"""
        return self.backend != "javascript"


# Singleton instance
_audio_recorder: Optional[AudioRecorder] = None


def get_audio_recorder(**kwargs) -> AudioRecorder:
    """Get or create audio recorder singleton"""
    global _audio_recorder
    if _audio_recorder is None:
        _audio_recorder = AudioRecorder(**kwargs)
    return _audio_recorder
