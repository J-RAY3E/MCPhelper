# Backend API

## Base URL

```
http://localhost:8000
```

## Endpoints

### Health Check

```
GET /
```

Response:
```json
{
  "status": "online",
  "name": "MCPDESK Backend"
}
```

### Command Execution

```
POST /command
```

Body:
```json
{
  "command": "your command here"
}
```

Response:
```json
{
  "type": "text",
  "content": "Response content",
  "mode": "chat"
}
```

### File Upload

```
POST /upload
```

Body: Multipart form data with file

Response:
```json
{
  "status": "success",
  "filename": "data.csv",
  "category": "datasets",
  "path": "datasets/data.csv"
}
```

### File Tree

```
GET /files
```

Response:
```json
{
  "tree": [
    {
      "id": "datasets",
      "label": "datasets",
      "children": [
        {"id": "data.csv", "label": "data.csv"}
      ]
    }
  ]
}
```

### Audio Transcription

```
POST /audio/transcribe
```

Body: Multipart form data with audio file

Response:
```json
{
  "success": true,
  "text": "transcribed text"
}
```

### Audio TTS

```
POST /audio/speak
```

Body:
```json
{
  "text": "Text to speak",
  "voice": "default",
  "rate": 150
}
```

## Error Responses

```json
{
  "type": "error",
  "content": "Error message"
}
```
