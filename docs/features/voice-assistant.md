# Voice Assistant

MCPDESK supports voice input using the WebAudio API and OpenAI Whisper.

## How It Works

1. User clicks microphone button
2. Browser records audio via WebAudio API
3. Audio is sent to backend
4. Whisper transcribes audio to text
5. Text is executed as a command

## Usage

### Starting Recording

Click the microphone button in the sidebar. The button will show:
- "🎤 Escuchar" - Ready
- "🎤 Grabando..." - Recording
- "⏳ Procesando..." - Processing

### Stopping Recording

Click the button again to stop. The audio will be:
- Transcribed by Whisper
- Sent to the agent pipeline
- Executed as a command

## Requirements

### Browser

- Chrome, Edge, or Firefox
- Microphone permission granted

### Backend

- Whisper model installed
- Sufficient disk space for model

## Models

Configure in `backend/audio/whisper_processor.py`:

| Model | Size | Speed | Accuracy |
|-------|------|-------|----------|
| tiny | ~75MB | Fastest | Low |
| base | ~140MB | Fast | Medium |
| small | ~500MB | Medium | Good |
| medium | ~1.5GB | Slow | High |
| large | ~3GB | Slowest | Highest |

Default: `base`

## Troubleshooting

### Microphone Permission

Grant microphone access in browser settings:
- Chrome: Settings > Privacy > Microphone
- Firefox: Settings > Permissions > Microphone

### Audio Quality

- Speak clearly
- Avoid background noise
- Keep microphone close
