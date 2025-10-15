# 🌐 Get Your Live URL in 2 Minutes!

Your AI Video Generator is ready to deploy and get a live URL that works from anywhere!

## ⚠️ Why GitHub Pages Doesn't Work

**GitHub Pages** only hosts static files (HTML, CSS, JavaScript). Your AI Video Generator is a **Python FastAPI backend application** that needs:
- Server-side processing
- Python runtime
- FFmpeg for video generation
- Background job processing
- API endpoints

**You need a platform that runs Python servers** → Use Railway, Render, or Fly.io instead!

---

## 🚀 Option 1: Railway (⭐ RECOMMENDED)

**Best for:** No cold starts, always-on, fastest deployment

### Steps:
1. Go to **https://railway.app/**
2. Sign up with GitHub (free)
3. Click "**New Project**" → "**Deploy from GitHub repo**"
4. Select repository: `**jeff99jackson99/ai-video-generator**`
5. Railway auto-detects configuration files
6. Click "**Deploy**"
7. Go to **Settings** → Click "**Generate Domain**"
8. **Done!** Your URL: `https://your-app.up.railway.app`

### Why Railway?
- ✅ **Free tier**: 500 hours/month
- ✅ **No cold starts**: App stays warm
- ✅ **Fast**: 2-minute deployment
- ✅ **Easy**: Auto-detects everything
- ✅ **HTTPS**: Automatic SSL certificate

---

## 🚀 Option 2: Render (Always Free)

**Best for:** Always free (with cold starts acceptable)

### Steps:
1. Go to **https://dashboard.render.com/**
2. Sign up with GitHub (free)
3. Click "**New**" → "**Web Service**"
4. Connect GitHub account
5. Select: `**jeff99jackson99/ai-video-generator**`
6. Render auto-detects `render.yaml`
7. Click "**Create Web Service**"
8. Wait 3-5 minutes
9. **Done!** Your URL: `https://ai-video-generator.onrender.com`

### Why Render?
- ✅ **Always free**: No time limits
- ✅ **Auto-deploy**: Updates from GitHub automatically
- ✅ **Docker**: Uses your Dockerfile
- ✅ **Reliable**: Very stable platform
- ⚠️ **Cold starts**: 30-second wake time after 15 min idle

---

## 🚀 Option 3: Fly.io (Good Performance)

**Best for:** Good performance, no cold starts

### Steps:
```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh

# Login
fly auth login

# Deploy
cd /Users/jeff/ai-video-generator
fly launch --copy-config

# Your URL: https://ai-video-generator.fly.dev
```

### Why Fly.io?
- ✅ **Free tier**: 3 shared VMs
- ✅ **Fast**: Good for video processing
- ✅ **Global**: Deploy close to users
- ✅ **No cold starts**: Always on

---

## 📋 Quick Comparison

| Platform | Free Tier | Cold Starts | Setup Difficulty | Best For |
|----------|-----------|-------------|------------------|----------|
| **Railway** | 500 hrs/mo | ❌ No | ⭐⭐⭐⭐⭐ Easiest | Quick & Easy |
| **Render** | Unlimited | ✅ Yes (30s) | ⭐⭐⭐⭐ Easy | Always Free |
| **Fly.io** | 3 VMs | ❌ No | ⭐⭐⭐ Medium | Performance |
| **Cloud Run** | 2M req/mo | ✅ Yes (5s) | ⭐⭐⭐ Medium | Scalable |

---

## 🎯 After Deployment

### 1. Test Your App
Visit: `https://your-url.com/healthz`

Should return:
```json
{"status": "healthy", "version": "0.1.0"}
```

### 2. Open the Web Interface
Visit: `https://your-url.com`

You'll see the beautiful AI Video Generator interface!

### 3. Create Your First Video
1. Enter a script (try the example below)
2. Choose options (TTS, captions, music)
3. Click "**Generate Video**"
4. Wait 2-5 minutes
5. Download your video!

### Example Script:
```
Welcome to the AI Video Generator!

This tool transforms scripts into professional videos.

It finds stunning visuals from free stock libraries.

AI creates natural voiceovers automatically.

Captions are perfectly synced with narration.

Background music sets the perfect mood.

Creating videos has never been easier!
```

### 4. Add API Keys (Optional)

Go to: `https://your-url.com/static/settings.html`

Add free API keys for better quality:
- **Gemini**: https://makersuite.google.com/app/apikey (free)
- **Pexels**: https://www.pexels.com/api/ (free)
- **Unsplash**: https://unsplash.com/developers (free)
- **Pixabay**: https://pixabay.com/api/docs/ (free)

All are **100% free** with generous limits!

---

## 💡 Tips for Free Tier

### Keep App Warm (Render Only)
Use a free uptime monitor to ping your app every 10 minutes:
- **UptimeRobot**: https://uptimerobot.com/
- Ping URL: `https://your-app.onrender.com/healthz`
- Prevents cold starts!

### Optimize Performance
Add these environment variables in platform dashboard:
```
MAX_CONCURRENT_JOBS=1
MAX_VIDEO_LENGTH_SECONDS=120
```

This limits resource usage on free tier.

### Monitor Usage
Check your platform dashboard to see:
- Hours used (Railway)
- Request counts (Cloud Run)
- Memory usage
- Build logs

---

## 🆘 Troubleshooting

### "Build Failed"
1. Check platform logs for errors
2. Ensure repository is public
3. Try deploying again (sometimes transient)

### "App Not Responding"
1. Check if build completed successfully
2. Look at application logs
3. Verify environment variables are set
4. For Render: First request takes 30s (cold start)

### "Out of Memory"
1. Set `MAX_CONCURRENT_JOBS=1`
2. Reduce `MAX_VIDEO_LENGTH_SECONDS=120`
3. Consider upgrading to paid tier for more memory

### "Video Generation Slow"
1. First video is slow (downloads AI models)
2. Subsequent videos are much faster
3. Free tiers have CPU/memory limits
4. This is normal behavior

---

## 📚 More Help

- **Complete Deployment Guide**: [DEPLOYMENT.md](DEPLOYMENT.md)
- **Quick 2-Minute Guide**: [QUICK_DEPLOY.md](QUICK_DEPLOY.md)
- **Main Documentation**: [README.md](README.md)
- **GitHub Issues**: https://github.com/jeff99jackson99/ai-video-generator/issues

---

## ✅ Summary

1. **Don't use GitHub Pages** (it's for static sites only)
2. **Use Railway** (easiest, recommended) or **Render** (always free)
3. **Deploy in 2 minutes** with one-click
4. **Get live URL** immediately
5. **Start creating videos** from anywhere!

**Ready?** Go to https://railway.app/ and deploy now! 🚀

---

Made with ❤️ - Now deployable anywhere!

