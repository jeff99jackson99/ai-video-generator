"""Video generation engine using MoviePy."""

import asyncio
from pathlib import Path
from typing import List, Dict, Optional, Callable
import random

from moviepy import (
    VideoFileClip,
    ImageClip,
    AudioFileClip,
    CompositeVideoClip,
    CompositeAudioClip,
    TextClip,
    concatenate_videoclips,
)
from moviepy.video.fx import FadeIn, FadeOut, Resize


class VideoGenerator:
    """Generates videos from scripts, media, voiceovers, and captions."""

    def __init__(
        self,
        output_dir: Path = Path("./output"),
        temp_dir: Path = Path("./data/temp")
    ):
        """Initialize video generator."""
        self.output_dir = output_dir
        self.temp_dir = temp_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)

        # Video settings
        self.resolution = (1920, 1080)
        self.fps = 30

    async def generate_video(
        self,
        job_id: str,
        scenes: List[Dict],
        media_files: List[Path],
        audio_path: Path,
        captions: Optional[List[Dict]] = None,
        background_music: Optional[Path] = None,
        progress_callback: Optional[Callable[[int], None]] = None
    ) -> Path:
        """
        Generate complete video.

        Args:
            job_id: Unique job identifier
            scenes: List of scene dictionaries with text and timing
            media_files: List of image/video paths to use
            audio_path: Path to voiceover audio
            captions: Optional caption data
            background_music: Optional background music path
            progress_callback: Optional callback for progress updates

        Returns:
            Path to generated video file
        """
        try:
            if progress_callback:
                progress_callback(10)

            # Create video clips from scenes and media
            video_clips = await self._create_scene_clips(scenes, media_files)

            if progress_callback:
                progress_callback(30)

            # Concatenate all clips
            final_video = concatenate_videoclips(video_clips, method="compose")

            if progress_callback:
                progress_callback(50)

            # Add voiceover audio
            voiceover_audio = AudioFileClip(str(audio_path))

            # Add background music if provided
            if background_music and background_music.exists():
                music_audio = AudioFileClip(str(background_music))
                # Mix voiceover and music
                final_audio = CompositeAudioClip([voiceover_audio, music_audio])
            else:
                final_audio = voiceover_audio

            # Set audio to video
            final_video = final_video.set_audio(final_audio)

            if progress_callback:
                progress_callback(70)

            # Add captions if provided
            if captions:
                final_video = self._add_captions_to_video(final_video, captions)

            if progress_callback:
                progress_callback(85)

            # Export video
            output_path = self.output_dir / f"{job_id}_video.mp4"

            final_video.write_videofile(
                str(output_path),
                fps=self.fps,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile=str(self.temp_dir / f"{job_id}_temp_audio.m4a"),
                remove_temp=True,
                preset='medium',
                threads=4
            )

            if progress_callback:
                progress_callback(100)

            # Clean up
            final_video.close()
            voiceover_audio.close()
            if background_music:
                music_audio.close()

            return output_path

        except Exception as e:
            raise Exception(f"Video generation failed: {e}")

    async def _create_scene_clips(
        self,
        scenes: List[Dict],
        media_files: List[Path]
    ) -> List[VideoFileClip]:
        """Create video clips for each scene."""
        clips = []

        for i, scene in enumerate(scenes):
            duration = scene.get('duration', 5)

            # Select media file for this scene
            media_index = i % len(media_files)
            media_path = media_files[media_index]

            # Create clip based on media type
            if media_path.suffix.lower() in ['.mp4', '.mov', '.avi']:
                # Video file
                clip = VideoFileClip(str(media_path))
                # Take only the needed duration
                clip = clip.subclip(0, min(duration, clip.duration))
                if clip.duration < duration:
                    # Loop if video is too short
                    loops = int(duration / clip.duration) + 1
                    clip = concatenate_videoclips([clip] * loops)
                    clip = clip.subclip(0, duration)
            else:
                # Image file
                clip = ImageClip(str(media_path), duration=duration)

            # Apply professional effects: resize + fade in/out
            clip = clip.with_effects([
                Resize(self.resolution),
                FadeIn(0.5),
                FadeOut(0.5)
            ])

            # Note: Ken Burns effect disabled for MoviePy 2.x compatibility
            # Will be re-added in future update with custom implementation

            clips.append(clip)

        return clips

    def _apply_ken_burns_effect(
        self,
        clip: ImageClip,
        duration: float
    ) -> ImageClip:
        """Apply Ken Burns (slow zoom) effect to image clip."""
        def zoom(t):
            # Gradually zoom from 100% to 110% over the duration
            factor = 1 + 0.1 * (t / duration)
            return factor

        # Apply zoom effect (simplified for compatibility)
        # Note: Dynamic resize not fully supported in MoviePy 2.x yet
        # Using static resize as fallback
        return clip

    def _add_captions_to_video(
        self,
        video: CompositeVideoClip,
        captions: List[Dict]
    ) -> CompositeVideoClip:
        """Add captions/subtitles to video."""
        caption_clips = []

        for caption in captions:
            text = caption['text']
            start = caption['start_time']
            end = caption['end_time']
            duration = end - start

            # Get caption style
            fontsize = caption.get('fontsize', 70)
            color = caption.get('color', 'white')
            stroke_color = caption.get('stroke_color', 'black')
            stroke_width = caption.get('stroke_width', 3)
            font = caption.get('font', 'Arial-Bold')

            # Create text clip
            try:
                txt_clip = TextClip(
                    text,
                    fontsize=fontsize,
                    color=color,
                    font=font,
                    stroke_color=stroke_color if stroke_color != 'none' else None,
                    stroke_width=stroke_width,
                    method='caption',
                    size=(self.resolution[0] * 0.9, None),
                    align='center'
                )

                # Position caption
                position = caption.get('position', ('center', 'bottom'))
                txt_clip = txt_clip.set_position(position)

                # Set timing
                txt_clip = txt_clip.set_start(start).set_duration(duration)

                # Add fade in/out for smooth caption appearance
                txt_clip = txt_clip.with_effects([
                    FadeIn(0.1),
                    FadeOut(0.1)
                ])

                caption_clips.append(txt_clip)

            except Exception as e:
                print(f"Error creating caption '{text}': {e}")
                continue

        # Composite video with captions
        if caption_clips:
            video = CompositeVideoClip([video] + caption_clips)

        return video

    def create_preview(
        self,
        job_id: str,
        media_files: List[Path],
        duration: float = 5.0
    ) -> Path:
        """Create a quick preview video from media files."""
        clips = []

        clip_duration = duration / len(media_files)

        for media_path in media_files[:5]:  # Max 5 clips for preview
            if media_path.suffix.lower() in ['.mp4', '.mov', '.avi']:
                clip = VideoFileClip(str(media_path))
                clip = clip.subclip(0, min(clip_duration, clip.duration))
            else:
                clip = ImageClip(str(media_path), duration=clip_duration)

            # Resize for preview
            clip = clip.with_effects([Resize(self.resolution)])
            clips.append(clip)

        # Concatenate clips
        preview_video = concatenate_videoclips(clips, method="compose")

        # Export preview
        preview_path = self.output_dir / f"{job_id}_preview.mp4"
        preview_video.write_videofile(
            str(preview_path),
            fps=30,
            codec='libx264',
            preset='ultrafast'
        )

        preview_video.close()
        return preview_path

    def get_video_info(self, video_path: Path) -> Dict[str, any]:
        """Get information about a video file."""
        clip = VideoFileClip(str(video_path))

        info = {
            'duration': clip.duration,
            'fps': clip.fps,
            'size': clip.size,
            'resolution': f"{clip.w}x{clip.h}",
            'aspect_ratio': clip.w / clip.h
        }

        clip.close()
        return info
