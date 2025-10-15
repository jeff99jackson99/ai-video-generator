#!/bin/bash

# AI Video Generator - Local Startup Script
# Quick start your video generator on M4 Mac

echo ""
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║                                                           ║"
echo "║       🎬  AI Video Generator - Local Server  🎬          ║"
echo "║                                                           ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# Check if Python 3.11 is installed
if ! command -v /opt/homebrew/bin/python3.11 &> /dev/null; then
    echo "❌ Python 3.11 not found. Installing..."
    brew install python@3.11
fi

# Check if FFmpeg is installed
if ! command -v ffmpeg &> /dev/null; then
    echo "❌ FFmpeg not found. Installing..."
    brew install ffmpeg
fi

# Check if dependencies are installed
if ! /opt/homebrew/bin/python3.11 -c "import fastapi" 2>/dev/null; then
    echo "📦 Installing dependencies..."
    /opt/homebrew/bin/python3.11 -m pip install -e .
fi

echo "✅ All dependencies ready!"
echo ""
echo "🚀 Starting AI Video Generator..."
echo ""
echo "📍 Server will be available at:"
echo "   👉  http://localhost:8000  👈"
echo ""
echo "⚙️  Settings page:"
echo "   http://localhost:8000/static/settings.html"
echo ""
echo "🛑  Press Ctrl+C to stop the server"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Start the server
/opt/homebrew/bin/python3.11 -m uvicorn src.app.web:app --host 0.0.0.0 --port 8000 --reload
