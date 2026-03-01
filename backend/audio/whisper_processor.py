"""
Whisper Processor - Speech-to-Text using OpenAI Whisper
100% offline processing
"""

import os
import tempfile
from typing import Dict, Any, Optional
from pathlib import Path


class WhisperProcessor:
    """
    Whisper-based speech-to-text processor for offline transcription.
    Supports multiple languages and various audio formats.
    """
    
    def __init__(self, model_name: str = "base", device: str = "cpu"):
        """
        Initialize Whisper processor.
        
        Args:
            model_name: Model size - tiny, base, small, medium, large
            device: Device to use - 'cpu' or 'cuda' (if GPU available)
        """
        self.model_name = model_name
        self.device = device
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load Whisper model (lazy loading)"""
        try:
            import whisper
            self.model = whisper.load_model(self.model_name, device=self.device)
            print(f"Whisper model '{self.model_name}' loaded successfully on {self.device}")
        except ImportError:
            print("Whisper not installed. Install with: pip install openai-whisper")
            self.model = None
        except Exception as e:
            print(f"Error loading Whisper model: {e}")
            self.model = None
    
    def transcribe_audio(self, audio_path: str, language: Optional[str] = None, 
                        task: str = "transcribe") -> Dict[str, Any]:
        """
        Transcribe audio file to text.
        
        Args:
            audio_path: Path to audio file
            language: Language code (e.g., 'en', 'es') or None for auto-detect
            task: 'transcribe' or 'translate'
            
        Returns:
            Dictionary with transcription results
        """
        if self.model is None:
            return {
                "success": False,
                "error": "Whisper model not loaded. Please install whisper: pip install openai-whisper"
            }
        
        try:
            # Prepare transcription options
            options = {
                "verbose": False,
                "task": task,
            }
            
            if language:
                options["language"] = language
            
            # Perform transcription
            result = self.model.transcribe(audio_path, **options)
            
            return {
                "success": True,
                "text": result["text"].strip(),
                "segments": result.get("segments", []),
                "language": result.get("language", language or "auto"),
                "duration": result.get("duration", 0)
            }
            
        except FileNotFoundError:
            return {
                "success": False,
                "error": f"Audio file not found: {audio_path}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Transcription error: {str(e)}"
            }
    
    def transcribe_audio_data(self, audio_data: bytes, sample_rate: int = 16000,
                             language: Optional[str] = None) -> Dict[str, Any]:
        """
        Transcribe raw audio data.
        
        Args:
            audio_data: Raw audio bytes
            sample_rate: Audio sample rate
            language: Language code or None for auto-detect
            
        Returns:
            Dictionary with transcription results
        """
        if self.model is None:
            return {
                "success": False,
                "error": "Whisper model not loaded"
            }
        
        try:
            import numpy as np
            import io
            import soundfile as sf
            
            # Convert bytes to numpy array
            audio_array = np.frombuffer(audio_data, dtype=np.float32)
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                sf.write(tmp.name, audio_array, sample_rate)
                tmp_path = tmp.name
            
            # Transcribe
            result = self.transcribe_audio(tmp_path, language=language)
            
            # Cleanup
            os.unlink(tmp_path)
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error processing audio data: {str(e)}"
            }
    
    def get_available_models(self) -> list:
        """Return list of available Whisper models"""
        return ["tiny", "base", "small", "medium", "large", "large-v2", "large-v3"]
    
    def is_loaded(self) -> bool:
        """Check if model is loaded"""
        return self.model is not None


# Singleton instance for global use
_whisper_processor: Optional[WhisperProcessor] = None


def get_whisper_processor(model_name: str = "base", device: str = "cpu") -> WhisperProcessor:
    """Get or create Whisper processor singleton"""
    global _whisper_processor
    if _whisper_processor is None:
        _whisper_processor = WhisperProcessor(model_name, device)
    return _whisper_processor


def transcribe(audio_path: str, language: Optional[str] = None) -> Dict[str, Any]:
    """Convenience function for quick transcription"""
    processor = get_whisper_processor()
    return processor.transcribe_audio(audio_path, language=language)
