"""
Audio Utilities - Helper functions for audio processing
"""

import os
import tempfile
import hashlib
from typing import Optional, Dict, Any, List
from pathlib import Path


class AudioUtils:
    """Utility class for audio file operations"""
    
    @staticmethod
    def validate_audio_file(filepath: str) -> Dict[str, Any]:
        """
        Validate audio file exists and is readable.
        
        Args:
            filepath: Path to audio file
            
        Returns:
            Dictionary with validation result
        """
        if not os.path.exists(filepath):
            return {
                "valid": False,
                "error": "File does not exist"
            }
        
        if not os.path.isfile(filepath):
            return {
                "valid": False,
                "error": "Path is not a file"
            }
        
        # Check file extension
        valid_extensions = ['.wav', '.mp3', '.ogg', '.flac', '.m4a', '.webm']
        ext = os.path.splitext(filepath)[1].lower()
        if ext not in valid_extensions:
            return {
                "valid": False,
                "error": f"Unsupported file format. Supported: {', '.join(valid_extensions)}"
            }
        
        # Check file size (max 100MB)
        file_size = os.path.getsize(filepath)
        max_size = 100 * 1024 * 1024  # 100MB
        if file_size > max_size:
            return {
                "valid": False,
                "error": f"File too large ({file_size / 1024 / 1024:.1f}MB). Max: 100MB"
            }
        
        if file_size == 0:
            return {
                "valid": False,
                "error": "File is empty"
            }
        
        return {
            "valid": True,
            "filepath": filepath,
            "filename": os.path.basename(filepath),
            "extension": ext,
            "size": file_size
        }
    
    @staticmethod
    def get_audio_info(filepath: str) -> Dict[str, Any]:
        """
        Get audio file information.
        
        Args:
            filepath: Path to audio file
            
        Returns:
            Dictionary with audio file info
        """
        validation = AudioUtils.validate_audio_file(filepath)
        if not validation.get("valid"):
            return validation
        
        try:
            import soundfile as sf
            info = sf.info(filepath)
            
            return {
                "valid": True,
                "filepath": filepath,
                "filename": os.path.basename(filepath),
                "duration": info.duration,
                "sample_rate": info.samplerate,
                "channels": info.channels,
                "format": info.format,
                "subtype": info.subtype,
                "size": os.path.getsize(filepath)
            }
        except ImportError:
            return {
                "valid": True,
                "filepath": filepath,
                "filename": os.path.basename(filepath),
                "size": os.path.getsize(filepath),
                "note": "Install soundfile for detailed info"
            }
        except Exception as e:
            return {
                "valid": False,
                "error": f"Error reading file: {str(e)}"
            }
    
    @staticmethod
    def convert_audio(input_path: str, output_path: str, 
                     format: str = "wav", sample_rate: int = 16000) -> Dict[str, Any]:
        """
        Convert audio file to different format.
        
        Args:
            input_path: Input audio file path
            output_path: Output audio file path
            format: Output format (wav, mp3, flac, ogg)
            sample_rate: Target sample rate
            
        Returns:
            Dictionary with conversion result
        """
        try:
            import soundfile as sf
            
            # Read audio
            data, sr = sf.read(input_path)
            
            # Resample if needed
            if sr != sample_rate:
                import numpy as np
                from scipy import signal
                
                # Calculate new length
                new_length = int(len(data) * sample_rate / sr)
                data = signal.resample(data, new_length)
                sr = sample_rate
            
            # Ensure mono if needed
            if len(data.shape) > 1:
                data = data.mean(axis=1)
            
            # Write output
            sf.write(output_path, data, sr)
            
            return {
                "success": True,
                "input": input_path,
                "output": output_path,
                "format": format,
                "sample_rate": sr
            }
        except ImportError:
            return {
                "success": False,
                "error": "Install soundfile and scipy for audio conversion"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Conversion error: {str(e)}"
            }
    
    @staticmethod
    def create_temp_filename(prefix: str = "audio", suffix: str = ".wav") -> str:
        """
        Create temporary audio file path.
        
        Args:
            prefix: Filename prefix
            suffix: File extension
            
        Returns:
            Temporary file path
        """
        temp_dir = tempfile.gettempdir()
        import uuid
        filename = f"{prefix}_{uuid.uuid4().hex[:8]}{suffix}"
        return os.path.join(temp_dir, filename)
    
    @staticmethod
    def calculate_audio_hash(filepath: str) -> str:
        """
        Calculate MD5 hash of audio file.
        
        Args:
            filepath: Path to audio file
            
        Returns:
            MD5 hash string
        """
        hash_md5 = hashlib.md5()
        try:
            with open(filepath, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            return f"error: {str(e)}"
    
    @staticmethod
    def get_supported_formats() -> List[str]:
        """Get list of supported audio formats"""
        return ['wav', 'mp3', 'ogg', 'flac', 'm4a', 'webm']
    
    @staticmethod
    def cleanup_temp_audio(prefix: str = "audio") -> int:
        """
        Clean up temporary audio files.
        
        Args:
            prefix: Filename prefix to match
            
        Returns:
            Number of files deleted
        """
        temp_dir = tempfile.gettempdir()
        deleted = 0
        
        try:
            for filename in os.listdir(temp_dir):
                if filename.startswith(prefix) and filename.endswith(('.wav', '.mp3', '.ogg', '.flac')):
                    filepath = os.path.join(temp_dir, filename)
                    try:
                        os.unlink(filepath)
                        deleted += 1
                    except Exception:
                        pass
        except Exception:
            pass
        
        return deleted


# Convenience functions
def validate_audio(filepath: str) -> Dict[str, Any]:
    """Validate audio file"""
    return AudioUtils.validate_audio_file(filepath)


def get_audio_info(filepath: str) -> Dict[str, Any]:
    """Get audio file information"""
    return AudioUtils.get_audio_info(filepath)


def convert_audio(input_path: str, output_path: str, 
                 format: str = "wav", sample_rate: int = 16000) -> Dict[str, Any]:
    """Convert audio file"""
    return AudioUtils.convert_audio(input_path, output_path, format, sample_rate)


def create_temp_audio(prefix: str = "audio", suffix: str = ".wav") -> str:
    """Create temporary audio file path"""
    return AudioUtils.create_temp_filename(prefix, suffix)
