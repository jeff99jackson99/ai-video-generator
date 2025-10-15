"""FastAPI web application for AI Video Generator."""

import asyncio
import json
from pathlib import Path
from typing import Optional, Dict, Any
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.core.config import Config
from src.core.job_manager import JobManager, JobStatus
from src.services.script_enhancer import ScriptEnhancer
from src.services.media_fetcher import MediaFetcher
from src.services.voiceover_manager import VoiceoverManager
from src.services.caption_generator import CaptionGenerator
from src.services.music_selector import MusicSelector
from src.services.video_generator import VideoGenerator
from src.services.video_quality_enhancer import VideoQualityEnhancer

# Initialize FastAPI app
app = FastAPI(
    title="AI Video Generator",
    description="Generate AI-powered videos from scripts with voiceovers and captions",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
job_manager = JobManager(Config.DATA_DIR)
script_enhancer = ScriptEnhancer(
    openai_api_key=Config.OPENAI_API_KEY,
    gemini_api_key=Config.GEMINI_API_KEY,
    groq_api_key=Config.GROQ_API_KEY
)
media_fetcher = MediaFetcher(
    pexels_key=Config.PEXELS_API_KEY,
    unsplash_key=Config.UNSPLASH_API_KEY,
    pixabay_key=Config.PIXABAY_API_KEY,
    cache_dir=Config.MEDIA_DIR
)
voiceover_manager = VoiceoverManager(Config.VOICEOVER_DIR)
caption_generator = CaptionGenerator()
music_selector = MusicSelector(
    pixabay_key=Config.PIXABAY_API_KEY,
    music_dir=Config.DATA_DIR / "music"
)
video_generator = VideoGenerator(
    output_dir=Config.OUTPUT_DIR,
    temp_dir=Config.DATA_DIR / "temp"
)
quality_enhancer = VideoQualityEnhancer(
    openai_api_key=Config.OPENAI_API_KEY
)

# Mount static files
static_dir = Path(__file__).parent / "static"
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


# Pydantic models
class GenerateRequest(BaseModel):
    script: str
    use_tts: bool = True
    voice: str = "default"
    add_captions: bool = True
    caption_style: str = "modern"
    add_music: bool = True
    mood: Optional[str] = "professional"


class SettingsRequest(BaseModel):
    openai_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    groq_api_key: Optional[str] = None
    pexels_api_key: Optional[str] = None
    unsplash_api_key: Optional[str] = None
    pixabay_api_key: Optional[str] = None


# Routes
@app.get("/")
async def root():
    """Serve the main page."""
    index_file = static_dir / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"message": "AI Video Generator API", "version": "0.1.0"}


@app.get("/healthz")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "0.1.0"}


@app.post("/api/generate")
async def generate_video(
    script: str = Form(...),
    use_tts: bool = Form(True),
    voice: str = Form("default"),
    add_captions: bool = Form(True),
    caption_style: str = Form("modern"),
    add_music: bool = Form(True),
    mood: Optional[str] = Form("professional"),
    voice_recording: Optional[UploadFile] = File(None),
    background_tasks: BackgroundTasks = None
):
    """
    Generate a video from a script.

    Args:
        script: The video script text
        use_tts: Use text-to-speech (if False, must upload voice recording)
        voice: Voice to use for TTS
        add_captions: Add captions to video
        caption_style: Caption style (modern, classic, minimal, bold)
        add_music: Add background music
        mood: Mood for music selection
        voice_recording: Optional audio file upload
    """
    try:
        # Create job
        options = {
            "use_tts": use_tts,
            "voice": voice,
            "add_captions": add_captions,
            "caption_style": caption_style,
            "add_music": add_music,
            "mood": mood
        }

        job_id = job_manager.create_job(script, options)

        # Save voice recording if provided
        if voice_recording:
            audio_data = await voice_recording.read()
            await voiceover_manager.save_recording(audio_data, job_id, format="mp3")

        # Start background processing
        if background_tasks:
            background_tasks.add_task(process_video_job, job_id)
        else:
            asyncio.create_task(process_video_job(job_id))

        return {
            "job_id": job_id,
            "status": "pending",
            "message": "Video generation started"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/status/{job_id}")
async def get_job_status(job_id: str):
    """Get the status of a video generation job."""
    job = job_manager.get_job(job_id)

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return {
        "job_id": job.job_id,
        "status": job.status.value,
        "progress": job.progress,
        "error": job.error,
        "output_file": job.output_file,
        "created_at": job.created_at,
        "updated_at": job.updated_at
    }


@app.get("/api/download/{job_id}")
async def download_video(job_id: str):
    """Download the generated video."""
    job = job_manager.get_job(job_id)

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.status != JobStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Video not ready yet")

    if not job.output_file:
        raise HTTPException(status_code=404, detail="Output file not found")

    video_path = Path(job.output_file)
    if not video_path.exists():
        raise HTTPException(status_code=404, detail="Video file not found")

    return FileResponse(
        video_path,
        media_type="video/mp4",
        filename=f"video_{job_id}.mp4"
    )


@app.post("/api/settings")
async def save_settings(settings: SettingsRequest):
    """Save user API keys and settings."""
    try:
        # In production, these should be stored securely per user
        # For now, we'll update the environment (session only)
        settings_file = Config.DATA_DIR / "user_settings.json"

        # Encrypt API keys before storing
        encrypted_settings = {}
        for key, value in settings.dict().items():
            if value:
                encrypted_settings[key] = Config.encrypt_api_key(value)

        settings_file.write_text(json.dumps(encrypted_settings, indent=2))

        # Update current session
        if settings.openai_api_key:
            Config.OPENAI_API_KEY = settings.openai_api_key
        if settings.gemini_api_key:
            Config.GEMINI_API_KEY = settings.gemini_api_key
        if settings.groq_api_key:
            Config.GROQ_API_KEY = settings.groq_api_key
        if settings.pexels_api_key:
            Config.PEXELS_API_KEY = settings.pexels_api_key
        if settings.unsplash_api_key:
            Config.UNSPLASH_API_KEY = settings.unsplash_api_key
        if settings.pixabay_api_key:
            Config.PIXABAY_API_KEY = settings.pixabay_api_key

        # Reinitialize services with new keys
        global script_enhancer, media_fetcher, music_selector
        script_enhancer = ScriptEnhancer(
            openai_api_key=Config.OPENAI_API_KEY,
            gemini_api_key=Config.GEMINI_API_KEY,
            groq_api_key=Config.GROQ_API_KEY
        )
        media_fetcher = MediaFetcher(
            pexels_key=Config.PEXELS_API_KEY,
            unsplash_key=Config.UNSPLASH_API_KEY,
            pixabay_key=Config.PIXABAY_API_KEY,
            cache_dir=Config.MEDIA_DIR
        )
        music_selector = MusicSelector(
            pixabay_key=Config.PIXABAY_API_KEY,
            music_dir=Config.DATA_DIR / "music"
        )

        return {"message": "Settings saved successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/settings")
async def get_settings():
    """Get current settings (without revealing API keys)."""
    settings_file = Config.DATA_DIR / "user_settings.json"

    if not settings_file.exists():
        return {
            "has_openai": bool(Config.OPENAI_API_KEY),
            "has_gemini": bool(Config.GEMINI_API_KEY),
            "has_groq": bool(Config.GROQ_API_KEY),
            "has_pexels": bool(Config.PEXELS_API_KEY),
            "has_unsplash": bool(Config.UNSPLASH_API_KEY),
            "has_pixabay": bool(Config.PIXABAY_API_KEY)
        }

    encrypted_settings = json.loads(settings_file.read_text())

    return {
        "has_openai": "openai_api_key" in encrypted_settings,
        "has_gemini": "gemini_api_key" in encrypted_settings,
        "has_groq": "groq_api_key" in encrypted_settings,
        "has_pexels": "pexels_api_key" in encrypted_settings,
        "has_unsplash": "unsplash_api_key" in encrypted_settings,
        "has_pixabay": "pixabay_api_key" in encrypted_settings
    }


@app.get("/api/jobs")
async def list_jobs(limit: int = 20):
    """List recent jobs."""
    jobs = job_manager.list_jobs(limit=limit)

    return {
        "jobs": [
            {
                "job_id": job.job_id,
                "status": job.status.value,
                "progress": job.progress,
                "created_at": job.created_at,
                "script_preview": job.script[:100] + "..." if len(job.script) > 100 else job.script
            }
            for job in jobs
        ]
    }


# Background task for video processing
async def process_video_job(job_id: str):
    """Process a video generation job in the background."""
    try:
        # Update status
        job_manager.update_job(job_id, status=JobStatus.PROCESSING, progress=5)

        job = job_manager.get_job(job_id)
        if not job:
            return

        script = job.script
        options = job.options

        # Step 1: Enhance script with AI
        job_manager.update_job(job_id, progress=5)
        print(f"🤖 Starting AI script enhancement...")
        job_manager.update_job(job_id, progress=10)
        
        enhanced_data = await script_enhancer.enhance_script(script)
        scenes = enhanced_data['scenes']
        keywords = enhanced_data['keywords']
        mood = options.get('mood', enhanced_data.get('mood', 'professional'))
        
        job_manager.update_job(job_id, progress=15)
        print(f"✅ Script enhanced! {len(scenes)} scenes, {len(keywords)} keywords")
        
        # Step 2: Fetch media with progress updates
        job_manager.update_job(job_id, progress=20)
        print(f"📸 Fetching {len(scenes)} images from Pexels...")
        job_manager.update_job(job_id, progress=25)
        
        media_files = await media_fetcher.search_and_download(keywords, count=len(scenes))
        
        job_manager.update_job(job_id, progress=35)
        print(f"✅ {len(media_files)} images downloaded!")

        if not media_files:
            raise Exception("No media files found")

        # Step 3: Generate or load voiceover with progress
        job_manager.update_job(job_id, progress=40)
        print(f"🎙️ Generating voiceover...")
        voiceover_path = Config.VOICEOVER_DIR / f"{job_id}_recording.mp3"
        
        if not voiceover_path.exists():
            # Generate TTS
            full_script = enhanced_data['enhanced_script']
            job_manager.update_job(job_id, progress=45)
            
            voiceover_path = await voiceover_manager.generate_tts(
                full_script,
                job_id,
                voice=options.get('voice', 'default')
            )
            job_manager.update_job(job_id, progress=50)
        
        # Process audio
        print(f"🔊 Processing audio...")
        voiceover_path = await voiceover_manager.process_audio(voiceover_path)
        job_manager.update_job(job_id, progress=52)
        
        # Sync scenes with audio timing
        scenes = await voiceover_manager.sync_audio_to_script(voiceover_path, scenes)
        job_manager.update_job(job_id, progress=54)
        print(f"✅ Voiceover ready! Duration: {voiceover_manager.get_audio_duration(voiceover_path):.1f}s")

        # Step 4: Generate captions with progress
        job_manager.update_job(job_id, progress=56)
        print(f"📝 Generating captions...")
        captions = None
        if options.get('add_captions', True):
            job_manager.update_job(job_id, progress=58)
            captions = await caption_generator.generate_captions_from_script(
                script,
                scenes,
                voiceover_manager.get_audio_duration(voiceover_path)
            )
            job_manager.update_job(job_id, progress=62)
            captions = caption_generator.prepare_captions_for_video(
                captions,
                style=options.get('caption_style', 'modern')
            )
            job_manager.update_job(job_id, progress=65)
            print(f"✅ {len(captions)} captions created!")
        
        # Step 5: Get background music
        job_manager.update_job(job_id, progress=68)
        print(f"🎵 Selecting background music...")
        music_path = None
        if options.get('add_music', True):
            music_path = await music_selector.select_music(
                mood=mood,
                duration=voiceover_manager.get_audio_duration(voiceover_path)
            )
            if music_path:
                job_manager.update_job(job_id, progress=70)
                music_path = music_selector.adjust_music_duration(
                    music_path,
                    voiceover_manager.get_audio_duration(voiceover_path)
                )
                print(f"✅ Background music ready!")
            job_manager.update_job(job_id, progress=72)

        # Step 6: Generate video with detailed progress
        job_manager.update_job(job_id, progress=75)
        print(f"🎬 Starting video assembly...")
        
        def update_progress(progress: int):
            """Real-time progress callback."""
            job_manager.update_job(job_id, progress=progress)
            print(f"📊 Progress: {progress}%")

        output_path = await video_generator.generate_video(
            job_id=job_id,
            scenes=scenes,
            media_files=media_files,
            audio_path=voiceover_path,
            captions=captions,
            background_music=music_path,
            progress_callback=update_progress
        )

        # Step 7: AI Quality Review (if OpenAI configured)
        if Config.OPENAI_API_KEY:
            job_manager.update_job(job_id, progress=98)
            print(f"🤖 Running AI quality analysis...")
            
            analysis = await quality_enhancer.analyze_video_quality(
                output_path,
                script,
                scenes,
                keywords
            )
            
            # Log suggestions for future improvements
            if analysis.get('suggestions'):
                print(f"💡 AI Suggestions: {analysis.get('overall_assessment', '')}")
                print(f"   Quality Score: {analysis.get('quality_score', 0)}/10")
                
                # Store suggestions in job metadata for user reference
                if analysis.get('quality_score', 10) < 8:
                    print(f"💡 AI recommends improvements for next video:")
                    print(f"   {analysis.get('next_iteration_tips', 'Try different keywords')}")
        
        # Mark as completed
        job_manager.update_job(
            job_id,
            status=JobStatus.COMPLETED,
            progress=100,
            output_file=str(output_path)
        )
        
        print(f"✅ VIDEO COMPLETE! Generated: {output_path.name}")

    except Exception as e:
        print(f"Error processing job {job_id}: {e}")
        job_manager.update_job(
            job_id,
            status=JobStatus.FAILED,
            error=str(e)
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=Config.APP_HOST, port=Config.APP_PORT)
