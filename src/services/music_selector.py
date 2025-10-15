"""Background music selection and management."""

import random
from pathlib import Path
from typing import Optional, List
import httpx


class MusicSelector:
    """Selects and manages background music for videos."""

    def __init__(
        self,
        pixabay_key: Optional[str] = None,
        music_dir: Path = Path("./data/music")
    ):
        """Initialize music selector."""
        self.pixabay_key = pixabay_key
        self.music_dir = music_dir
        self.music_dir.mkdir(parents=True, exist_ok=True)

        # Preset mood to genre mapping
        self.mood_genres = {
            "upbeat": ["pop", "electronic", "happy"],
            "calm": ["ambient", "chill", "acoustic"],
            "professional": ["corporate", "business", "tech"],
            "inspirational": ["motivational", "uplifting", "cinematic"],
            "dramatic": ["epic", "cinematic", "intense"],
            "educational": ["background", "soft", "neutral"]
        }

    async def select_music(
        self,
        mood: str = "professional",
        duration: float = 60.0
    ) -> Optional[Path]:
        """
        Select appropriate background music based on mood.

        Args:
            mood: The mood/tone of the video
            duration: Required duration in seconds

        Returns:
            Path to music file or None
        """
        # Try to fetch from online sources
        if self.pixabay_key:
            try:
                music_path = await self._fetch_pixabay_music(mood)
                if music_path:
                    return music_path
            except Exception as e:
                print(f"Error fetching music from Pixabay: {e}")

        # Use preset/local music if available
        local_music = await self._get_local_music(mood)
        if local_music:
            return local_music

        # Return None if no music available (video will be generated without music)
        return None

    async def _fetch_pixabay_music(self, mood: str) -> Optional[Path]:
        """
        Fetch music from Pixabay.

        Note: Pixabay's music API might be limited. This is a placeholder
        for when/if they provide a proper API endpoint.
        """
        # Pixabay doesn't have a dedicated free music API endpoint yet
        # This would need to be implemented when available
        # For now, we'll use local/preset music
        return None

    async def _get_local_music(self, mood: str) -> Optional[Path]:
        """Get music from local preset library."""
        # Check if we have any local music files
        music_files = list(self.music_dir.glob("*.mp3"))

        if not music_files:
            # Create a note about music
            readme = self.music_dir / "README.txt"
            readme.write_text(
                "Place royalty-free background music files here.\n"
                "Recommended sources:\n"
                "- YouTube Audio Library (free)\n"
                "- Free Music Archive\n"
                "- Incompetech (Kevin MacLeod)\n"
                "- Bensound\n\n"
                "Organize by mood: upbeat_*.mp3, calm_*.mp3, etc."
            )
            return None

        # Try to find music matching the mood
        genres = self.mood_genres.get(mood, ["background"])

        for genre in genres:
            matching = [f for f in music_files if genre in f.stem.lower()]
            if matching:
                return random.choice(matching)

        # Return random music if no mood match
        return random.choice(music_files)

    async def download_free_music(
        self,
        sources: List[str] = None
    ) -> List[Path]:
        """
        Download free music from Creative Commons sources.

        This is a helper function to populate the local music library.
        """
        if sources is None:
            sources = [
                # Add direct links to royalty-free music here
                # These would be Creative Commons licensed tracks
            ]

        downloaded = []

        async with httpx.AsyncClient() as client:
            for url in sources:
                try:
                    response = await client.get(url, timeout=30.0)
                    response.raise_for_status()

                    # Extract filename from URL
                    filename = url.split("/")[-1]
                    if not filename.endswith(".mp3"):
                        filename += ".mp3"

                    file_path = self.music_dir / filename
                    file_path.write_bytes(response.content)
                    downloaded.append(file_path)

                except Exception as e:
                    print(f"Error downloading {url}: {e}")

        return downloaded

    def adjust_music_duration(
        self,
        music_path: Path,
        target_duration: float,
        fade_in: float = 2.0,
        fade_out: float = 3.0
    ) -> Path:
        """
        Adjust music duration to match video length.

        Args:
            music_path: Path to original music file
            target_duration: Target duration in seconds
            fade_in: Fade in duration in seconds
            fade_out: Fade out duration in seconds

        Returns:
            Path to adjusted music file
        """
        from pydub import AudioSegment

        # Load music
        music = AudioSegment.from_file(music_path)
        music_duration = len(music) / 1000.0  # Convert to seconds

        # If music is longer than needed, trim it
        if music_duration > target_duration:
            # Trim from the end
            music = music[:int(target_duration * 1000)]

        # If music is shorter, loop it
        elif music_duration < target_duration:
            loops_needed = int(target_duration / music_duration) + 1
            music = music * loops_needed
            music = music[:int(target_duration * 1000)]

        # Apply fade in and fade out
        if fade_in > 0:
            music = music.fade_in(int(fade_in * 1000))
        if fade_out > 0:
            music = music.fade_out(int(fade_out * 1000))

        # Reduce volume to 30% so it doesn't overpower voiceover
        music = music - 12  # Reduce by 12dB

        # Save adjusted music
        adjusted_path = music_path.parent / f"{music_path.stem}_adjusted.mp3"
        music.export(adjusted_path, format="mp3", bitrate="192k")

        return adjusted_path
