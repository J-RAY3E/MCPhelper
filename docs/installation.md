# Installation Guide

## Prerequisites

- Python 3.10 or higher
- OpenAI API key (or compatible LLM endpoint)
- 4GB+ RAM recommended
- Microphone (for voice features)

## System Requirements

### Windows
- Windows 10 or later
- Visual C++ Redistributable (for some audio libraries)

### macOS
- macOS 10.15 (Catalina) or later

### Linux
- Ubuntu 20.04 or later
- libportaudio2 (for audio features)

## Step-by-Step Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd MCPDESK
```

###  Environment

```bash2. Create Virtual
# Using venv
python -m venv .venv

# Activate on Windows
.venv\Scripts\activate

# Activate on Linux/Mac
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Playwright (Optional)

Required for web scraping features:

```bash
playwright install chromium
```

### 5. Install Audio Dependencies (Optional)

For voice assistant features on Windows:

```bash
pip install pywin32
```

## Verification

Test your installation:

```bash
# Test backend imports
cd backend
python -c "from main import app; print('Backend OK')"

# Test frontend imports
cd ../frontend
python -c "from app import ui; print('Frontend OK')"
```

## Common Issues

### Module Not Found Errors

Ensure you're running from the correct directory and your virtual environment is activated.

### Audio Permission Issues

On macOS, you may need to grant microphone permissions:
```bash
System Preferences > Security & Privacy > Privacy > Microphone
```

### Port Already in Use

If ports 8000 or 8501 are in use, modify the port in:
- Backend: `backend/main.py`
- Frontend: `frontend/app.py`
