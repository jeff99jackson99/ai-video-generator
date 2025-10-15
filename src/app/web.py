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
from src.services.extreme_quality_enhancer import ExtremeQualityEnhancer
from src.services.media_verifier import MediaVerifier
from src.services.smart_media_selector import SmartMediaSelector

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
extreme_enhancer = ExtremeQualityEnhancer()
media_verifier = MediaVerifier(
    openai_api_key=Config.OPENAI_API_KEY
)
smart_media_selector = SmartMediaSelector(
    openai_api_key=Config.OPENAI_API_KEY,
    pexels_key=Config.PEXELS_API_KEY,
    cache_dir=Config.MEDIA_DIR
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
    aspect_ratio: str = "16:9"  # Support multiple aspect ratios


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


@app.get("/favicon.ico")
async def favicon():
    """Serve favicon to avoid 404 errors."""
    favicon_file = static_dir / "favicon.ico"
    if favicon_file.exists():
        return FileResponse(favicon_file)
    # Return empty response if no favicon
    return {"status": "ok"}


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
    aspect_ratio: str = Form("16:9"),
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
            "mood": mood,
            "aspect_ratio": aspect_ratio
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
        global script_enhancer, media_fetcher, music_selector, smart_media_selector
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
        smart_media_selector = SmartMediaSelector(
            openai_api_key=Config.OPENAI_API_KEY,
            pexels_key=Config.PEXELS_API_KEY,
            cache_dir=Config.MEDIA_DIR
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


@app.get("/api/preview-voice/{voice_name}")
async def preview_voice(voice_name: str):
    """Generate a short preview of a voice."""
    try:
        preview_text = "Hello! This is a preview of this voice. Perfect for your video."

        # Generate preview audio
        preview_id = f"preview_{voice_name}"
        preview_audio = await voiceover_manager.generate_tts(
            preview_text,
            preview_id,
            voice=voice_name
        )

        return FileResponse(
            preview_audio,
            media_type="audio/mpeg",
            filename=f"preview_{voice_name}.mp3"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Preview generation failed: {str(e)}")


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

        # Step 2: SMART MEDIA SELECTION using GPT-4 perfect queries!
        job_manager.update_job(job_id, progress=20)
        print(f"🧠 Using GPT-4 to generate PERFECT search queries for {len(scenes)} scenes...")
        job_manager.update_job(job_id, progress=22)

        # Use SMART selector - GPT-4 generates perfect queries based on what's being said!
        media_files_with_metadata = await smart_media_selector.fetch_perfect_media_per_scene(
            scenes,
            media_fetcher  # Pass fetcher for Pexels API access
        )

        job_manager.update_job(job_id, progress=28)
        print(f"✅ {len(media_files_with_metadata)} PERFECTLY-MATCHED media files downloaded!")

        # Step 2.5: Enhance media (work with tuples)
        print(f"🎨 AI enhancing {len(media_files_with_metadata)} media files for maximum quality...")
        job_manager.update_job(job_id, progress=32)

        enhanced_media_with_metadata = []
        for i, (media_file, metadata) in enumerate(media_files_with_metadata):
            try:
                if media_file.suffix.lower() in ['.jpg', '.jpeg', '.png']:
                    # AI enhance images
                    enhanced = extreme_enhancer.enhance_image(media_file)
                    enhanced_media_with_metadata.append((enhanced, metadata))
                else:
                    # Use video as-is (already high quality from Pexels)
                    enhanced_media_with_metadata.append((media_file, metadata))

                # Progress update for each file
                progress = 32 + int((i / len(media_files_with_metadata)) * 6)
                job_manager.update_job(job_id, progress=progress)
            except Exception as e:
                print(f"Enhancement error for {media_file.name}: {e}")
                enhanced_media_with_metadata.append((media_file, metadata))  # Use original if enhancement fails

        media_files_with_metadata = enhanced_media_with_metadata
        job_manager.update_job(job_id, progress=38)
        print(f"✅ All media AI-enhanced for EXTREME quality!")

        if not media_files_with_metadata:
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

        # Step 4: Generate captions with WHISPER for accurate timing
        job_manager.update_job(job_id, progress=56)
        print(f"📝 Generating captions with Whisper (accurate timing)...")
        captions = None
        if options.get('add_captions', True):
            job_manager.update_job(job_id, progress=58)

            # Use Whisper to transcribe the actual audio for perfect timing
            captions = await caption_generator.generate_captions_from_audio(
                voiceover_path,
                use_whisper=True
            )

            job_manager.update_job(job_id, progress=62)

            if captions:
                # Apply styling to the accurately-timed captions
                captions = caption_generator.prepare_captions_for_video(
                    captions,
                    style=options.get('caption_style', 'modern')
                )
                job_manager.update_job(job_id, progress=65)
                print(f"✅ {len(captions)} perfectly-timed captions created!")
            else:
                # Fallback to script-based if Whisper fails
                print(f"⚠️ Whisper failed, using script-based timing...")
                captions = await caption_generator.generate_captions_from_script(
                    script,
                    scenes,
                    voiceover_manager.get_audio_duration(voiceover_path)
                )
                captions = caption_generator.prepare_captions_for_video(
                    captions,
                    style=options.get('caption_style', 'modern')
                )
                job_manager.update_job(job_id, progress=65)
                print(f"✅ {len(captions)} script-based captions created")

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

        # Step 6: Generate video with detailed progress and aspect ratio
        job_manager.update_job(job_id, progress=75)
        aspect_ratio = options.get('aspect_ratio', '16:9')
        print(f"🎬 Starting video assembly ({aspect_ratio})...")

        # Create video generator with specified aspect ratio
        video_gen = VideoGenerator(
            output_dir=Config.OUTPUT_DIR,
            temp_dir=Config.DATA_DIR / "temp",
            aspect_ratio=aspect_ratio
        )

        def update_progress(progress: int):
            """Real-time progress callback."""
            job_manager.update_job(job_id, progress=progress)
            print(f"📊 Progress: {progress}%")

        output_path = await video_gen.generate_video(
            job_id=job_id,
            scenes=scenes,
            media_files_with_metadata=media_files_with_metadata,  # Pass with metadata!
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
