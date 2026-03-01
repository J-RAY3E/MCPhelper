# Audio Module for MCPDESK
# Speech-to-Text (Whisper) and Text-to-Speech (TTS) capabilities

from .whisper_processor import WhisperProcessor
from .tts_processor import TTSProcessor
from .audio_recorder import AudioRecorder
from .audio_utils import AudioUtils

__all__ = [
    'WhisperProcessor',
    'TTSProcessor', 
    'AudioRecorder',
    'AudioUtils'
]
