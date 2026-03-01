"""
Audio Components - NiceGUI UI components for audio functionality
Provides recording, playback, transcription, and TTS UI elements
"""

import os
import tempfile
from typing import Optional, Callable, Dict, Any
from pathlib import Path


class AudioComponents:
    """
    Collection of NiceGUI audio UI components.
    Provides interactive audio controls for MCPDESK.
    """
    
    @staticmethod
    def create_record_button(on_record: Optional[Callable] = None,
                           on_stop: Optional[Callable] = None,
                           label: str = "Record") -> 'ui.row':
        """
        Create a record button with visual feedback.
        
        Args:
            on_record: Callback when recording starts
            on_stop: Callback when recording stops
            label: Button label
            
        Returns:
            NiceGUI row with record button
        """
        from nicegui import ui
        
        is_recording = [False]
        button = [None]
        
        def toggle_recording():
            is_recording[0] = not is_recording[0]
            if is_recording[0]:
                button[0].props('color=red')
                button[0].set_text('Stop Recording')
                if on_record:
                    on_record()
            else:
                button[0].props('color=primary')
                button[0].set_text(label)
                if on_stop:
                    on_stop()
        
        button[0] = ui.button(
            label,
            on_click=toggle_recording,
            icon='mic'
        ).props('round')
        
        return button[0]
    
    @staticmethod
    def create_audio_player(audio_path: str, 
                           show_controls: bool = True) -> 'ui.audio':
        """
        Create an audio player component.
        
        Args:
            audio_path: Path to audio file
            show_controls: Whether to show playback controls
            
        Returns:
            NiceGUI audio element
        """
        from nicegui import ui
        
        audio = ui.audio(audio_path)
        
        if show_controls:
            audio.props('controls')
        
        return audio
    
    @staticmethod
    def create_recording_indicator() -> 'ui.badge':
        """
        Create a visual recording indicator (pulsing red dot).
        
        Returns:
            NiceGUI badge component
        """
        from nicegui import ui
        
        badge = ui.badge(
            '● Recording',
            color='red',
            text_color='white'
        ).props('floating')
        
        return badge
    
    @staticmethod
    def create_transcription_viewer(transcription: str,
                                   language: str = "auto",
                                   confidence: float = 1.0) -> 'ui.card':
        """
        Create a transcription display card.
        
        Args:
            transcription: Transcribed text
            language: Detected language
            confidence: Confidence score
            
        Returns:
            NiceGUI card with transcription
        """
        from nicegui import ui
        
        with ui.card().classes('w-full p-4'):
            with ui.row().classes('items-center justify-between w-full'):
                ui.label('🎤 Transcription').classes('font-bold text-lg')
                ui.badge(
                    language.upper(),
                    color='grey'
                ).props('floating')
            
            ui.separator()
            
            ui.label(transcription).classes('text-wrap w-full')
            
            with ui.row().classes('text-xs text-grey-6 mt-2'):
                ui.label(f'Confidence: {confidence:.0%}')
    
    @staticmethod
    def create_tts_controls(on_speak: Optional[Callable] = None,
                          on_stop: Optional[Callable] = None) -> 'ui.card':
        """
        Create TTS control panel.
        
        Args:
            on_speak: Callback for speak action
            on_stop: Callback for stop action
            
        Returns:
            NiceGUI card with TTS controls
        """
        from nicegui import ui
        
        with ui.card().classes('w-full p-4'):
            ui.label('🔊 Text-to-Speech').classes('font-bold text-lg')
            
            with ui.row().classes('w-full gap-2'):
                ui.button(
                    'Speak',
                    on_click=on_speak if on_speak else lambda: None,
                    icon='volume_up'
                ).props('round color=primary')
                
                ui.button(
                    'Stop',
                    on_click=on_stop if on_stop else lambda: None,
                    icon='stop'
                ).props('round')
            
            with ui.row().classes('w-full mt-2 gap-4'):
                with ui.column().classes('flex-1'):
                    ui.label('Speed').classes('text-xs')
                    rate_slider = ui.slider(
                        min=50, 
                        max=300, 
                        value=150
                    ).classes('w-full')
                    ui.label('150 WPM').classes('text-xs text-grey-6')
                
                with ui.column().classes('flex-1'):
                    ui.label('Volume').classes('text-xs')
                    volume_slider = ui.slider(
                        min=0, 
                        max=100, 
                        value=80
                    ).classes('w-full')
                    ui.label('80%').classes('text-xs text-grey-6')
        
        return {
            'rate_slider': rate_slider,
            'volume_slider': volume_slider
        }
    
    @staticmethod
    def create_audio_uploader(on_upload: Callable[[str], None],
                            accepted_types: list = ['.wav', '.mp3', '.ogg', '.flac']) -> 'ui.upload':
        """
        Create an audio file uploader.
        
        Args:
            on_upload: Callback with uploaded file path
            accepted_types: List of accepted file extensions
            
        Returns:
            NiceGUI upload component
        """
        from nicegui import ui, events
        
        upload = ui.upload(
            on_upload=lambda e: AudioComponents._handle_upload(e, on_upload),
            multiple=False,
            label='Upload Audio',
            accept=','.join(accepted_types)
        ).props('accept=".wav,.mp3,.ogg,.flac"')
        
        return upload
    
    @staticmethod
    def _handle_upload(e: events.UploadEventArguments, callback: Callable[[str], None]):
        """Handle file upload"""
        # Save to temporary file
        temp_dir = tempfile.gettempdir()
        filepath = os.path.join(temp_dir, e.name)
        
        with open(filepath, 'wb') as f:
            f.write(e.content.read())
        
        callback(filepath)
    
    @staticmethod
    def create_audio_settings_panel(on_save: Optional[Callable] = None) -> 'ui.card':
        """
        Create audio settings configuration panel.
        
        Args:
            on_save: Callback when settings are saved
            
        Returns:
            NiceGUI card with settings
        """
        from nicegui import ui
        
        settings = {
            'whisper_model': 'base',
            'language': 'auto',
            'tts_voice': 'default',
            'tts_rate': 150,
            'tts_volume': 80,
            'sample_rate': 16000
        }
        
        with ui.card().classes('w-full p-4'):
            ui.label('⚙️ Audio Settings').classes('font-bold text-lg')
            
            ui.separator()
            
            # Whisper settings
            with ui.row().classes('w-full items-center'):
                ui.label('Whisper Model:').classes('w-32')
                model_select = ui.select(
                    label='Model',
                    options=['tiny', 'base', 'small', 'medium', 'large'],
                    value='base'
                ).classes('flex-1')
            
            with ui.row().classes('w-full items-center'):
                ui.label('Language:').classes('w-32')
                lang_select = ui.select(
                    label='Language',
                    options=['auto', 'en', 'es', 'fr', 'de', 'it', 'pt', 'zh', 'ja', 'ko'],
                    value='auto'
                ).classes('flex-1')
            
            ui.separator()
            
            # TTS settings
            with ui.row().classes('w-full items-center'):
                ui.label('TTS Voice:').classes('w-32')
                voice_select = ui.select(
                    label='Voice',
                    options=['default', 'male', 'female'],
                    value='default'
                ).classes('flex-1')
            
            with ui.row().classes('w-full items-center'):
                ui.label('Sample Rate:').classes('w-32')
                sample_select = ui.select(
                    label='Sample Rate',
                    options=['8000', '16000', '22050', '44100'],
                    value='16000'
                ).props('clearable')
                .classes('flex-1')
            
            if on_save:
                ui.button('Save Settings', on_click=lambda: on_save(settings)).props('color=primary')
        
        return {
            'model': model_select,
            'language': lang_select,
            'voice': voice_select,
            'sample_rate': sample_select
        }
    
    @staticmethod
    def create_audio_toolbar(recording_callback: Optional[Callable] = None,
                           upload_callback: Optional[Callable] = None,
                           tts_callback: Optional[Callable] = None,
                           settings_callback: Optional[Callable] = None) -> 'ui.row':
        """
        Create a complete audio toolbar with all controls.
        
        Args:
            recording_callback: Callback for record button
            upload_callback: Callback for upload button
            tts_callback: Callback for TTS button
            settings_callback: Callback for settings button
            
        Returns:
            NiceGUI row with toolbar
        """
        from nicegui import ui
        
        with ui.row().classes('w-full gap-2'):
            # Record button
            ui.button(
                '🎤 Record',
                on_click=recording_callback if recording_callback else lambda: None,
                icon='mic'
            ).props('round color=primary')
            
            # Upload button
            ui.button(
                '📁 Upload',
                on_click=upload_callback if upload_callback else lambda: None,
                icon='upload_file'
            ).props('round')
            
            # TTS button
            ui.button(
                '🔊 Speak',
                on_click=tts_callback if tts_callback else lambda: None,
                icon='volume_up'
            ).props('round')
            
            # Settings button
            ui.button(
                '⚙️',
                on_click=settings_callback if settings_callback else lambda: None,
                icon='settings'
            ).props('round flat')


class AudioState:
    """
    State management for audio components.
    Keeps track of recording state, current audio, etc.
    """
    
    def __init__(self):
        self.is_recording = False
        self.current_audio_path: Optional[str] = None
        self.transcription_history: list = []
        self.tts_busy = False
        
    def start_recording(self):
        """Mark recording as started"""
        self.is_recording = True
    
    def stop_recording(self):
        """Mark recording as stopped"""
        self.is_recording = False
    
    def set_current_audio(self, path: str):
        """Set current audio file path"""
        self.current_audio_path = path
    
    def add_transcription(self, text: str, language: str = "auto"):
        """Add transcription to history"""
        self.transcription_history.append({
            'text': text,
            'language': language
        })
    
    def clear_history(self):
        """Clear transcription history"""
        self.transcription_history = []


# Global state instance
audio_state = AudioState()
