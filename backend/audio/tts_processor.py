"""
TTS Processor - Text-to-Speech using pyttsx3
100% offline processing for Windows, macOS, and Linux
"""

import os
import tempfile
import platform
from typing import Dict, Any, Optional, List


class TTSProcessor:
    """
    Text-to-Speech processor using pyttsx3 for offline synthesis.
    Uses native system voices (SAPI5 on Windows, NSSpeechSynthesizer on macOS, espeak on Linux).
    """
    
    def __init__(self):
        """Initialize TTS engine"""
        self.engine = None
        self.voices = []
        self.default_voice = None
        self.default_rate = 150  # words per minute
        self.default_volume = 1.0
        self._initialize_engine()
    
    def _initialize_engine(self):
        """Initialize pyttsx3 engine"""
        try:
            import pyttsx3
            self.engine = pyttsx3.init()
            self._load_voices()
            print(f"TTS engine initialized successfully on {platform.system()}")
        except ImportError:
            print("pyttsx3 not installed. Install with: pip install pyttsx3")
            self.engine = None
        except Exception as e:
            print(f"Error initializing TTS engine: {e}")
            self.engine = None
    
    def _load_voices(self):
        """Load available voices"""
        if self.engine is None:
            return
        
        try:
            self.voices = self.engine.getProperty('voices')
            if self.voices:
                self.default_voice = self.voices[0].id
        except Exception as e:
            print(f"Error loading voices: {e}")
            self.voices = []
    
    def set_voice(self, voice_id: str) -> bool:
        """
        Set voice by ID.
        
        Args:
            voice_id: Voice ID string
            
        Returns:
            True if successful, False otherwise
        """
        if self.engine is None:
            return False
        
        try:
            voice_ids = [v.id for v in self.voices]
            if voice_id in voice_ids:
                self.engine.setProperty('voice', voice_id)
                return True
            return False
        except Exception as e:
            print(f"Error setting voice: {e}")
            return False
    
    def set_rate(self, rate: int):
        """
        Set speech rate.
        
        Args:
            rate: Words per minute (default 150)
        """
        if self.engine is None:
            return
        
        try:
            self.engine.setProperty('rate', rate)
            self.default_rate = rate
        except Exception as e:
            print(f"Error setting rate: {e}")
    
    def set_volume(self, volume: float):
        """
        Set volume level.
        
        Args:
            volume: Volume level 0.0 to 1.0 (default 1.0)
        """
        if self.engine is None:
            return
        
        try:
            volume = max(0.0, min(1.0, volume))
            self.engine.setProperty('volume', volume)
            self.default_volume = volume
        except Exception as e:
            print(f"Error setting volume: {e}")
    
    def speak(self, text: str, blocking: bool = True) -> Dict[str, Any]:
        """
        Speak text immediately (blocking or non-blocking).
        
        Args:
            text: Text to speak
            blocking: If True, wait for completion
            
        Returns:
            Dictionary with result status
        """
        if self.engine is None:
            return {
                "success": False,
                "error": "TTS engine not initialized"
            }
        
        try:
            if blocking:
                self.engine.say(text)
                self.engine.runAndWait()
                return {
                    "success": True,
                    "text": text,
                    "duration": self._estimate_duration(text)
                }
            else:
                self.engine.say(text)
                return {
                    "success": True,
                    "text": text,
                    "note": "Non-blocking mode - use stop() to halt"
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Speech error: {str(e)}"
            }
    
    def save_to_file(self, text: str, filename: Optional[str] = None,
                    voice_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Convert text to speech and save to audio file.
        
        Args:
            text: Text to convert
            filename: Output file path (optional, defaults to temp file)
            voice_id: Voice ID to use
            
        Returns:
            Dictionary with file path and result
        """
        if self.engine is None:
            return {
                "success": False,
                "error": "TTS engine not initialized"
            }
        
        try:
            # Set voice if specified
            if voice_id:
                self.set_voice(voice_id)
            
            # Generate filename if not provided
            if filename is None:
                temp_dir = tempfile.gettempdir()
                filename = os.path.join(temp_dir, "tts_output.mp3")
            
            # Save to file
            self.engine.save_to_file(text, filename)
            self.engine.runAndWait()
            
            return {
                "success": True,
                "audio_file": filename,
                "duration": self._estimate_duration(text)
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error saving to file: {str(e)}"
            }
    
    def stop(self):
        """Stop current speech"""
        if self.engine is None:
            return
        
        try:
            self.engine.stop()
        except Exception as e:
            print(f"Error stopping: {e}")
    
    def get_voices(self) -> List[Dict[str, Any]]:
        """
        Get list of available voices.
        
        Returns:
            List of voice dictionaries
        """
        voices_list = []
        for voice in self.voices:
            voices_list.append({
                "id": voice.id,
                "name": voice.name,
                "languages": getattr(voice, 'languages', []),
                "gender": getattr(voice, 'gender', 'unknown')
            })
        return voices_list
    
    def _estimate_duration(self, text: str) -> float:
        """Estimate speech duration in seconds"""
        words = len(text.split())
        return (words / self.default_rate) * 60
    
    def is_available(self) -> bool:
        """Check if TTS engine is available"""
        return self.engine is not None


# Singleton instance
_tts_processor: Optional[TTSProcessor] = None


def get_tts_processor() -> TTSProcessor:
    """Get or create TTS processor singleton"""
    global _tts_processor
    if _tts_processor is None:
        _tts_processor = TTSProcessor()
    return _tts_processor


def speak(text: str, blocking: bool = True) -> Dict[str, Any]:
    """Convenience function for quick speech"""
    processor = get_tts_processor()
    return processor.speak(text, blocking=blocking)


def speak_to_file(text: str, filename: Optional[str] = None) -> Dict[str, Any]:
    """Convenience function to save speech to file"""
    processor = get_tts_processor()
    return processor.save_to_file(text, filename=filename)
