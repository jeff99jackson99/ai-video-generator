# 🚀 Deployment Guide

Deploy your AI Video Generator to the cloud and get a live URL!

## ⚠️ Important Note About GitHub Pages

**GitHub Pages DOES NOT work for this app** because it only hosts static files (HTML/CSS/JS), while this is a Python FastAPI backend application that needs server-side processing.

Use one of the deployment options below instead.

---

## 🎯 Recommended: One-Click Deployments (Free)

### Option 1: Railway (Easiest) ⭐ RECOMMENDED

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/ai-video-generator?referralCode=YOUR_CODE)

**Pros:**
- ✅ Free tier: 500 hours/month
- ✅ One-click deployment
- ✅ Automatic HTTPS
- ✅ Easy environment variable management
- ✅ Supports Docker

**Steps:**
1. Click the "Deploy on Railway" button
2. Connect your GitHub account
3. Select the `jeff99jackson99/ai-video-generator` repository
4. Add optional API keys in environment variables
5. Wait 2-3 minutes for deployment
6. Get your live URL: `https://your-app.railway.app`

**Manual Railway Deployment:**
```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Initialize and deploy
cd ai-video-generator
railway init
railway up
```

---

### Option 2: Render (Most Reliable)

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/jeff99jackson99/ai-video-generator)

**Pros:**
- ✅ Generous free tier
- ✅ Uses Docker
- ✅ Automatic deployments from GitHub
- ✅ Free SSL certificates
- ✅ Very stable

**Steps:**
1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click "New" → "Web Service"
3. Connect GitHub and select `ai-video-generator`
4. Render will auto-detect the `render.yaml` file
5. Add optional API keys in environment variables
6. Click "Create Web Service"
7. Your URL: `https://ai-video-generator.onrender.com`

**Note:** Free tier spins down after 15 minutes of inactivity (cold start takes ~30 seconds).

---

### Option 3: Fly.io (Good Performance)

**Pros:**
- ✅ Free tier: 3 shared-cpu VMs
- ✅ Fast global deployment
- ✅ Docker support
- ✅ Good for video processing

**Steps:**
```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh

# Login
fly auth login

# Deploy from repo directory
cd ai-video-generator
fly launch --copy-config --now

# Your URL: https://ai-video-generator.fly.dev
```

**Configuration:** The `fly.toml` file is already included.

---

### Option 4: Google Cloud Run (Scalable)

**Pros:**
- ✅ Free tier: 2 million requests/month
- ✅ Scales to zero (no cost when idle)
- ✅ Fast deployment
- ✅ Google infrastructure

**Steps:**
```bash
# Install Google Cloud SDK
# Visit: https://cloud.google.com/sdk/docs/install

# Login and set project
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# Deploy
cd ai-video-generator
gcloud run deploy ai-video-generator \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated

# Your URL: https://ai-video-generator-xxxxx-uc.a.run.app
```

---

### Option 5: Heroku (Classic)

[![Deploy to Heroku](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/jeff99jackson99/ai-video-generator)

**Pros:**
- ✅ Easy to use
- ✅ Well-documented
- ✅ Popular platform

**Cons:**
- ⚠️ Free tier removed (starts at $5/month for eco dynos)

**Steps:**
1. Click "Deploy to Heroku" button above
2. Set app name
3. Add optional API keys
4. Click "Deploy app"
5. Your URL: `https://your-app-name.herokuapp.com`

---

## 🔧 Configuration for All Platforms

### Required Environment Variables
```bash
APP_HOST=0.0.0.0
APP_PORT=8000  # Or use $PORT for Railway/Heroku
DEBUG=false
SECRET_KEY=your_random_secret_key_here
```

### Optional API Keys (Free Tier Available)
```bash
# AI Services (Optional - free alternatives available)
GEMINI_API_KEY=your_gemini_key
GROQ_API_KEY=your_groq_key

# Media Services (Optional - placeholders used if not set)
PEXELS_API_KEY=your_pexels_key
UNSPLASH_API_KEY=your_unsplash_key
PIXABAY_API_KEY=your_pixabay_key
```

**Get Free API Keys:**
- Gemini: https://makersuite.google.com/app/apikey
- Groq: https://console.groq.com/keys
- Pexels: https://www.pexels.com/api/
- Unsplash: https://unsplash.com/developers
- Pixabay: https://pixabay.com/api/docs/

---

## 📊 Platform Comparison

| Platform | Free Tier | Cold Start | Setup | Best For |
|----------|-----------|------------|-------|----------|
| **Railway** | 500 hrs/mo | ❌ No | ⭐⭐⭐⭐⭐ Easiest | Quick deployment |
| **Render** | Always free | ✅ Yes (30s) | ⭐⭐⭐⭐ Easy | Stability |
| **Fly.io** | 3 VMs | ❌ No | ⭐⭐⭐ Medium | Performance |
| **Cloud Run** | 2M req/mo | ✅ Yes (2-5s) | ⭐⭐⭐ Medium | Scalability |
| **Heroku** | ❌ None | ❌ No | ⭐⭐⭐⭐ Easy | Classic choice |

---

## 🎬 After Deployment

1. **Test Your Deployment**
   - Visit: `https://your-app-url.com/healthz`
   - Should return: `{"status": "healthy"}`

2. **Use the Web Interface**
   - Open: `https://your-app-url.com`
   - Enter a script and generate your first video!

3. **Add API Keys (Optional)**
   - Go to: `https://your-app-url.com/static/settings.html`
   - Add your free API keys for better quality

4. **Monitor Usage**
   - Check platform dashboard for usage stats
   - Free tiers are generous for personal use

---

## ⚡ Performance Tips

### For Free Tiers

1. **Reduce Cold Starts** (Render)
   - Keep app active with a ping service (e.g., UptimeRobot)
   - Ping `/healthz` every 10 minutes

2. **Optimize Video Processing**
   - Keep videos under 60 seconds on free tier
   - Use lower resolution if needed
   - Limit to 1 concurrent job

3. **Storage Considerations**
   - Generated videos are ephemeral
   - Download immediately after generation
   - Consider adding cloud storage (S3, Cloudinary)

---

## 🐳 Docker Deployment (Self-Hosted)

If you have your own server:

```bash
# Pull and run
docker pull ghcr.io/jeff99jackson99/ai-video-generator:latest
docker run -p 8000:8000 \
  -e GEMINI_API_KEY=your_key \
  -v ./data:/app/data \
  -v ./output:/app/output \
  ghcr.io/jeff99jackson99/ai-video-generator:latest
```

Or use Docker Compose:
```bash
cd ai-video-generator
docker-compose up -d
```

---

## 🔒 Security Notes

1. **API Keys**: Always use environment variables, never commit keys
2. **SECRET_KEY**: Generate a strong random key for production
3. **HTTPS**: All recommended platforms provide free SSL
4. **Rate Limiting**: Consider adding rate limiting for public deployments

---

## 🆘 Troubleshooting

### Deployment Fails
- Check platform logs for errors
- Ensure Dockerfile builds locally: `docker build -t test .`
- Verify all dependencies in `pyproject.toml`

### App Crashes
- Check memory limits (video processing is memory-intensive)
- Reduce MAX_CONCURRENT_JOBS to 1 on free tier
- Monitor logs for specific errors

### Slow Performance
- First video generation downloads AI models (one-time, ~1-2 min)
- Subsequent videos are faster
- Free tiers have CPU/memory limits
- Consider upgrading for heavy usage

### Cold Starts (Render)
- Expected behavior on free tier
- App spins down after 15 min inactivity
- First request takes 30-60s to wake up
- Use ping service to keep alive

---

## 📚 Next Steps

1. ✅ Deploy to your chosen platform
2. ✅ Get your live URL
3. ✅ Test with the example script from README
4. ✅ Add API keys for best quality
5. ✅ Share your creations!

---

## 💡 Recommended Setup

**For Personal Use:**
- Use **Railway** (easiest, no cold starts)
- Add free API keys
- Upgrade if you need more hours

**For Public/Demo:**
- Use **Render** (stable, always free)
- Accept cold starts
- Add uptime monitoring

**For Production:**
- Use **Google Cloud Run** or **Fly.io**
- Add proper monitoring
- Consider paid tier for better performance

---

**Need Help?** Open an issue on [GitHub](https://github.com/jeff99jackson99/ai-video-generator/issues)

