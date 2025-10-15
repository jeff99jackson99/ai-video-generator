# 🚀 Quick Start Guide

Get your AI Video Generator running in 5 minutes!

## 1. Install Dependencies

```bash
# Install Python dependencies
pip install -e .

# Install FFmpeg (required for video processing)
# macOS:
brew install ffmpeg

# Or check if already installed:
ffmpeg -version
```

## 2. Run the Application

```bash
# Start the server
python -m src.app

# Or use Make:
make dev
```

The app will start at: **http://localhost:8000**

## 3. Create Your First Video

1. Open http://localhost:8000 in your browser
2. Enter your video script (example below)
3. Choose your options:
   - ✅ Use AI Text-to-Speech (or upload your voice)
   - ✅ Add AI-Generated Captions
   - ✅ Add Background Music
4. Click "🎬 Generate Video"
5. Wait 2-5 minutes for processing
6. Download your video!

### Example Script

```
Welcome to the AI Video Generator!

This amazing tool transforms your scripts into professional videos.

It automatically finds relevant images and videos from free sources.

AI generates voiceovers and captions for you.

Background music sets the perfect mood.

Creating videos has never been this easy!
```

## 4. Optional: Add API Keys for Better Quality

Go to **Settings (⚙️)** and add free API keys:

- **Gemini**: https://makersuite.google.com/app/apikey
- **Pexels**: https://www.pexels.com/api/
- **Unsplash**: https://unsplash.com/developers
- **Pixabay**: https://pixabay.com/api/docs/

All keys are **100% free** with generous limits!

## 5. Tips for Best Results

- **Script Length**: 5-10 sentences work best (30-90 seconds)
- **Clear Topics**: Specific subjects get better visuals
- **Natural Language**: Write how you'd speak
- **Keywords**: Include visual keywords (e.g., "office", "sunset", "technology")

## Troubleshooting

### "FFmpeg not found"
```bash
# Install FFmpeg:
brew install ffmpeg  # macOS
# or
sudo apt-get install ffmpeg  # Linux
```

### "Module not found"
```bash
# Reinstall dependencies:
pip install -e ".[dev]"
```

### Video takes too long
- First video generation installs AI models (one-time)
- Subsequent videos are much faster
- Typical generation time: 2-5 minutes

## What Happens Behind the Scenes?

1. **AI Enhancement** (10s): Gemini improves your script
2. **Media Search** (20s): Finds relevant photos/videos
3. **Voiceover** (30s): Generates or processes audio
4. **Captions** (10s): Creates synced subtitles
5. **Video Assembly** (60-120s): MoviePy creates final video
6. **Export** (30s): Renders HD MP4

Total: 2-5 minutes ⏱️

## Next Steps

- 📖 Read the full [README.md](README.md)
- ⚙️ Configure API keys in Settings
- 🎨 Try different caption styles
- 🎵 Experiment with music moods
- 🎙️ Record your own voice

---

**Need Help?** Check [GitHub Issues](https://github.com/jeff99jackson99/ai-video-generator/issues)
