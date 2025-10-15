# 🎬 AI Video Generator

Create professional AI-powered videos from scripts with automated visuals, voiceovers, captions, and background music using free and open-source AI services.

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## ✨ Features

- 🤖 **AI Script Enhancement** - Automatically improve scripts with Google Gemini or Groq
- 🎨 **Automatic Media Search** - Find relevant images/videos from Pexels, Unsplash, Pixabay
- 🎙️ **Dual Voiceover Options**:
  - Record your own voice directly in browser
  - Use free AI text-to-speech (Coqui TTS, gTTS)
- 📝 **AI-Generated Captions** - Automatic subtitle generation with multiple styles
- 🎵 **Background Music** - Add royalty-free music matching video mood
- 🎞️ **Professional Video Output** - HD (1920x1080) videos with transitions and effects
- 🌐 **Modern Web Interface** - Beautiful, responsive UI
- 🔒 **Privacy First** - All API keys encrypted and stored locally
- 🆓 **100% Free Options** - Works without any paid services

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- FFmpeg (for video processing)
- Git

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/jeff99jackson99/ai-video-generator.git
cd ai-video-generator
```

2. **Install dependencies**
```bash
make setup
# Or manually:
pip install -e .
```

3. **Configure environment** (optional)
```bash
cp .env.example .env
# Edit .env with your API keys (all optional)
```

4. **Run the application**
```bash
make dev
# Or:
python -m src.app
```

5. **Open in browser**
```
http://localhost:8000
```

## 🎯 Usage

### Basic Workflow

1. **Write Your Script**
   - Enter your video script in the text area
   - The AI will automatically enhance it

2. **Choose Voiceover**
   - Option A: Record your own voice
   - Option B: Use AI text-to-speech

3. **Configure Options**
   - Enable/disable captions
   - Choose caption style
   - Select video mood for music
   - Add background music

4. **Generate Video**
   - Click "Generate Video"
   - Wait for processing (progress bar shows status)
   - Download when complete

### API Keys (Optional)

All services work without API keys using free alternatives. Add keys for enhanced quality:

- **Google Gemini**: Free tier, 15 requests/min → [Get Key](https://makersuite.google.com/app/apikey)
- **Groq**: Free, fast inference → [Get Key](https://console.groq.com/keys)
- **Pexels**: Unlimited free photos/videos → [Get Key](https://www.pexels.com/api/)
- **Unsplash**: Free high-quality photos → [Get Key](https://unsplash.com/developers)
- **Pixabay**: Free media, no attribution → [Get Key](https://pixabay.com/api/docs/)

Configure in Settings page (⚙️).

## 🏗️ Architecture

```
ai-video-generator/
├── src/
│   ├── app/
│   │   ├── web.py              # FastAPI application
│   │   ├── static/             # Frontend HTML/CSS/JS
│   │   │   ├── index.html      # Main interface
│   │   │   └── settings.html   # API key configuration
│   ├── services/
│   │   ├── script_enhancer.py  # AI script enhancement
│   │   ├── media_fetcher.py    # Stock media APIs
│   │   ├── voiceover_manager.py # Voice recording + TTS
│   │   ├── caption_generator.py # Subtitle generation
│   │   ├── music_selector.py   # Background music
│   │   └── video_generator.py  # MoviePy video creation
│   └── core/
│       ├── config.py           # Configuration
│       └── job_manager.py      # Async job queue
├── tests/                      # Pytest test suite
├── data/                       # Media cache & temp files
├── output/                     # Generated videos
└── .github/workflows/          # CI/CD pipelines
```

## 🔧 Development

### Commands

```bash
make setup          # Install dependencies
make dev            # Run development server
make test           # Run tests
make lint           # Run linter
make fmt            # Format code
make docker/build   # Build Docker image
make docker/run     # Run in Docker
```

### Running Tests

```bash
pytest tests/ -v --cov=src
```

### Docker Deployment

```bash
# Build image
docker build -t ai-video-generator .

# Run container
docker run -p 8000:8000 -v $(pwd)/data:/app/data -v $(pwd)/output:/app/output ai-video-generator
```

Or use Docker Compose:

```bash
docker-compose up
```

## 📋 API Endpoints

### Video Generation

**POST** `/api/generate`
```bash
curl -X POST http://localhost:8000/api/generate \
  -F "script=Your video script here" \
  -F "use_tts=true" \
  -F "add_captions=true" \
  -F "add_music=true"
```

**GET** `/api/status/{job_id}`
```bash
curl http://localhost:8000/api/status/your-job-id
```

**GET** `/api/download/{job_id}`
```bash
curl -O http://localhost:8000/api/download/your-job-id
```

### Settings

**POST** `/api/settings` - Save API keys
**GET** `/api/settings` - Check configured services
**GET** `/api/jobs` - List recent jobs

## 🎨 Caption Styles

- **Modern**: Bold white text with black stroke (default)
- **Classic**: Yellow text with black stroke
- **Minimal**: Clean white text, no stroke
- **Bold**: Large text with semi-transparent background

## 🎵 Music Moods

- Professional
- Upbeat
- Calm
- Inspirational
- Dramatic
- Educational

## 🔐 Security

- API keys encrypted with Fernet (cryptography library)
- Keys stored locally in `data/.key`
- Never transmitted over network
- Secure per-session configuration

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📝 License

MIT License - see [LICENSE](LICENSE) file

## 🙏 Credits

### Free Services Used
- **Google Gemini** - AI script enhancement
- **Groq** - Fast AI inference
- **Pexels** - Stock photos/videos
- **Unsplash** - High-quality photos
- **Pixabay** - Free media library
- **Coqui TTS** - Open-source text-to-speech
- **gTTS** - Google Text-to-Speech
- **Whisper** - Speech-to-text transcription

### Libraries
- **FastAPI** - Web framework
- **MoviePy** - Video editing
- **Pydub** - Audio processing
- **Pillow** - Image processing

## 🐛 Troubleshooting

### FFmpeg not found
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt-get install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html
```

### Import errors
```bash
# Reinstall dependencies
pip install -e ".[dev]"
```

### Video generation slow
- Reduce video resolution in config
- Use fewer scenes
- Disable captions for faster processing
- Check available system resources

### API rate limits
- Gemini: 15 requests/minute (free tier)
- Solution: Add multiple API keys or use Groq fallback

## 📚 Examples

### Example 1: Simple Video
```python
script = "Welcome to AI Video Generator. Create amazing videos with AI."
# Upload to web interface → Generate → Download
```

### Example 2: With Voice Recording
1. Record your narration
2. Upload MP3/WAV file
3. AI adds visuals, captions, and music automatically

### Example 3: API Usage
```python
import requests

response = requests.post('http://localhost:8000/api/generate', data={
    'script': 'Your amazing script here',
    'use_tts': True,
    'add_captions': True,
    'mood': 'inspirational'
})

job_id = response.json()['job_id']
print(f"Job created: {job_id}")
```

## 🗺️ Roadmap

- [ ] Video templates
- [ ] Multiple video formats (Square, Portrait, Landscape)
- [ ] Advanced transitions and effects
- [ ] Background music library
- [ ] Batch video generation
- [ ] Video editing interface
- [ ] Cloud deployment option
- [ ] Voice cloning support

## 💬 Support

- 📧 Issues: [GitHub Issues](https://github.com/jeff99jackson99/ai-video-generator/issues)
- 💡 Discussions: [GitHub Discussions](https://github.com/jeff99jackson99/ai-video-generator/discussions)

---

Made with ❤️ using free and open-source AI services

