"""Voiceover management with recording and TTS options."""

import asyncio
from pathlib import Path
from typing import Optional, List
import subprocess


class VoiceoverManager:
    """Manages voiceovers - both user recordings and TTS."""

    def __init__(self, storage_dir: Path = Path("./data/voiceovers")):
        """Initialize voiceover manager."""
        self.storage_dir = storage_dir
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    async def save_recording(
        self,
        audio_data: bytes,
        job_id: str,
        format: str = "mp3"
    ) -> Path:
        """Save user's voice recording."""
        filename = f"{job_id}_recording.{format}"
        file_path = self.storage_dir / filename

        file_path.write_bytes(audio_data)
        return file_path

    async def generate_tts(
        self,
        text: str,
        job_id: str,
        voice: str = "default",
        use_gtts: bool = True
    ) -> Path:
        """Generate text-to-speech with natural-sounding voices."""
        filename = f"{job_id}_tts.mp3"
        file_path = self.storage_dir / filename
        
        # Try Edge TTS first - FREE Microsoft voices, very natural!
        try:
            print(f"🎙️ Generating voiceover with Edge TTS (Microsoft) - Natural {voice} voice...")
            return await self._generate_edge_tts(text, file_path, voice)
        except Exception as e:
            print(f"Edge TTS error: {e}, trying Coqui TTS")
        
        # Try Coqui TTS second
        try:
            print(f"🎙️ Generating voiceover with Coqui TTS (voice: {voice})...")
            return await self._generate_coqui_tts(text, file_path, voice)
        except Exception as e:
            print(f"Coqui TTS not available: {e}, using gTTS")
        
        # Fallback to gTTS (robotic but reliable)
        if use_gtts:
            try:
                from gtts import gTTS
                print(f"🎙️ Generating voiceover with gTTS (robotic fallback)...")
                tts = gTTS(text=text, lang='en', slow=False)
                tts.save(str(file_path))
                print(f"✅ Voiceover generated with gTTS")
                return file_path
            except Exception as e:
                print(f"gTTS error: {e}")

        # Try Coqui TTS as alternative
        try:
            return await self._generate_coqui_tts(text, file_path, voice)
        except Exception as e:
            print(f"Coqui TTS error: {e}")
        # If all fail, create silent audio as fallback
        return await self._create_silent_audio(file_path, duration=5)
    
    async def _generate_edge_tts(
        self,
        text: str,
        output_path: Path,
        voice: str
    ) -> Path:
        """
        Generate TTS using Microsoft Edge TTS (FREE, very natural voices).
        
        Edge TTS voices are 100% free and sound like real people!
        """
        try:
            import edge_tts
            
            # Select natural voice based on preference
            voice_map = {
                "male": "en-US-GuyNeural",  # Natural American male
                "female": "en-US-AriaNeural",  # Natural American female
                "default": "en-US-GuyNeural"
            }
            
            edge_voice = voice_map.get(voice, voice_map["male"])
            
            print(f"🎙️ Using Microsoft Edge TTS voice: {edge_voice} (sounds like real person!)")
            
            # Generate speech
            communicate = edge_tts.Communicate(text, edge_voice)
            await communicate.save(str(output_path))
            
            print(f"✅ Natural voiceover generated with Edge TTS!")
            return output_path
            
        except Exception as e:
            raise Exception(f"Edge TTS generation failed: {e}")
    
    async def _generate_coqui_tts(
        self,
        text: str,
        output_path: Path,
        voice: str
    ) -> Path:
        """Generate TTS using Coqui TTS with male/female voice selection."""
        try:
            from TTS.api import TTS
            
            # Select model based on voice preference
            if voice == "female":
                model_name = "tts_models/en/ljspeech/tacotron2-DDC"
            elif voice == "male":
                # Use multi-speaker model for male voice
                model_name = "tts_models/en/vctk/vits"
                speaker = "p226"  # Male speaker
            else:
                # Default to female
                model_name = "tts_models/en/ljspeech/tacotron2-DDC"
            
            print(f"🎙️ Loading Coqui TTS model: {model_name}...")
            tts = TTS(model_name=model_name, progress_bar=False, gpu=False)
            
            # Generate speech
            if voice == "male" and model_name == "tts_models/en/vctk/vits":
                tts.tts_to_file(text=text, file_path=str(output_path), speaker=speaker)
            else:
                tts.tts_to_file(text=text, file_path=str(output_path))
            
            print(f"✅ High-quality voiceover generated!")
            return output_path
            
        except Exception as e:
            raise Exception(f"Coqui TTS generation failed: {e}")

    async def _create_silent_audio(
        self,
        output_path: Path,
        duration: int = 5
    ) -> Path:
        """Create silent audio file as fallback."""
        try:
            # Use ffmpeg to create silent audio
            cmd = [
                "ffmpeg", "-f", "lavfi", "-i",
                f"anullsrc=r=44100:cl=stereo",
                "-t", str(duration),
                "-q:a", "9", "-acodec", "libmp3lame",
                str(output_path), "-y"
            ]

            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await process.communicate()
            return output_path

        except Exception as e:
            raise Exception(f"Failed to create silent audio: {e}")

    async def process_audio(
        self,
        audio_path: Path,
        normalize: bool = True,
        remove_silence: bool = False
    ) -> Path:
        """Process audio file - normalize volume, remove silence, etc."""
        from pydub import AudioSegment
        from pydub.effects import normalize as pydub_normalize

        # Load audio
        audio = AudioSegment.from_file(audio_path)

        # Normalize audio levels
        if normalize:
            audio = pydub_normalize(audio)

        # Remove silence from beginning and end
        if remove_silence:
            # Detect non-silent parts
            non_silent = self._detect_non_silent(audio)
            if non_silent:
                start, end = non_silent[0][0], non_silent[-1][1]
                audio = audio[start:end]

        # Save processed audio
        processed_path = audio_path.parent / f"{audio_path.stem}_processed.mp3"
        audio.export(processed_path, format="mp3", bitrate="192k")

        return processed_path

    def _detect_non_silent(
        self,
        audio: 'AudioSegment',
        silence_threshold: int = -40,
        chunk_size: int = 10
    ) -> List[tuple]:
        """Detect non-silent chunks in audio."""
        from pydub.silence import detect_nonsilent

        return detect_nonsilent(
            audio,
            min_silence_len=chunk_size,
            silence_thresh=silence_threshold
        )

    def get_audio_duration(self, audio_path: Path) -> float:
        """Get duration of audio file in seconds."""
        from pydub import AudioSegment

        audio = AudioSegment.from_file(audio_path)
        return len(audio) / 1000.0  # Convert milliseconds to seconds

    async def sync_audio_to_script(
        self,
        audio_path: Path,
        script_scenes: List[dict]
    ) -> List[dict]:
        """Sync audio timestamps with script scenes."""
        total_duration = self.get_audio_duration(audio_path)

        # Simple approach: divide audio equally among scenes
        scene_duration = total_duration / len(script_scenes)

        synced_scenes = []
        for i, scene in enumerate(script_scenes):
            synced_scene = scene.copy()
            synced_scene['audio_start'] = i * scene_duration
            synced_scene['audio_end'] = (i + 1) * scene_duration
            synced_scene['duration'] = scene_duration
            synced_scenes.append(synced_scene)

        return synced_scenes
