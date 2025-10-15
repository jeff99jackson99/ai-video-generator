"""AI caption generation service with Whisper and subtitle generation."""

import asyncio
from pathlib import Path
from typing import List, Dict, Optional
import subprocess


class CaptionGenerator:
    """Generates captions and subtitles for videos."""
    
    def __init__(self):
        """Initialize caption generator."""
        pass
    
    async def generate_captions_from_audio(
        self,
        audio_path: Path,
        use_whisper: bool = True
    ) -> List[Dict[str, any]]:
        """
        Generate captions from audio file using Whisper.
        
        Returns list of caption segments with timestamps.
        """
        if use_whisper:
            try:
                return await self._transcribe_with_whisper(audio_path)
            except Exception as e:
                print(f"Whisper transcription error: {e}")
        
        # Fallback: return empty captions
        return []
    
    async def generate_captions_from_script(
        self,
        script: str,
        scenes: List[Dict],
        total_duration: float
    ) -> List[Dict[str, any]]:
        """
        Generate caption segments from script and scene timing.
        
        Returns:
            List of caption segments with text, start_time, end_time
        """
        captions = []
        
        for i, scene in enumerate(scenes):
            # Break scene text into smaller caption chunks (words or phrases)
            text = scene.get('text', '')
            words = text.split()
            
            # Scene timing
            scene_start = scene.get('audio_start', i * 5)
            scene_end = scene.get('audio_end', (i + 1) * 5)
            scene_duration = scene_end - scene_start
            
            # Create word-by-word captions for more engaging effect
            if words:
                word_duration = scene_duration / len(words)
                
                for j, word in enumerate(words):
                    caption = {
                        'text': word,
                        'start_time': scene_start + (j * word_duration),
                        'end_time': scene_start + ((j + 1) * word_duration),
                        'style': 'word'  # word, sentence, or full
                    }
                    captions.append(caption)
        
        return captions
    
    async def _transcribe_with_whisper(
        self,
        audio_path: Path
    ) -> List[Dict[str, any]]:
        """Transcribe audio using OpenAI Whisper."""
        try:
            import whisper
            
            # Load Whisper model (base is good balance of speed/accuracy)
            model = whisper.load_model("base")
            
            # Transcribe with word-level timestamps
            result = model.transcribe(
                str(audio_path),
                word_timestamps=True,
                language="en"
            )
            
            captions = []
            for segment in result.get('segments', []):
                # Get word-level timestamps if available
                if 'words' in segment:
                    for word_data in segment['words']:
                        captions.append({
                            'text': word_data['word'].strip(),
                            'start_time': word_data['start'],
                            'end_time': word_data['end'],
                            'style': 'word'
                        })
                else:
                    # Fall back to segment-level
                    captions.append({
                        'text': segment['text'].strip(),
                        'start_time': segment['start'],
                        'end_time': segment['end'],
                        'style': 'sentence'
                    })
            
            return captions
            
        except Exception as e:
            raise Exception(f"Whisper transcription failed: {e}")
    
    def create_srt_file(
        self,
        captions: List[Dict[str, any]],
        output_path: Path
    ) -> Path:
        """Create SRT subtitle file from caption data."""
        srt_content = []
        
        for i, caption in enumerate(captions, 1):
            start_time = self._format_srt_time(caption['start_time'])
            end_time = self._format_srt_time(caption['end_time'])
            text = caption['text']
            
            srt_content.append(f"{i}")
            srt_content.append(f"{start_time} --> {end_time}")
            srt_content.append(text)
            srt_content.append("")  # Blank line between entries
        
        # Write SRT file
        output_path.write_text("\n".join(srt_content))
        return output_path
    
    def _format_srt_time(self, seconds: float) -> str:
        """Format time in SRT format (HH:MM:SS,mmm)."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
    
    def get_caption_style_config(self, style: str = "modern") -> Dict[str, any]:
        """
        Get caption styling configuration for MoviePy.
        
        Styles: modern, classic, minimal, bold
        """
        styles = {
            "modern": {
                "fontsize": 70,
                "color": "white",
                "stroke_color": "black",
                "stroke_width": 3,
                "font": "Arial-Bold",
                "method": "caption",
                "align": "center",
                "bg_color": "transparent"
            },
            "classic": {
                "fontsize": 50,
                "color": "yellow",
                "stroke_color": "black",
                "stroke_width": 2,
                "font": "Arial",
                "method": "caption",
                "align": "center",
                "bg_color": "transparent"
            },
            "minimal": {
                "fontsize": 60,
                "color": "white",
                "stroke_color": "none",
                "stroke_width": 0,
                "font": "Helvetica",
                "method": "caption",
                "align": "center",
                "bg_color": "transparent"
            },
            "bold": {
                "fontsize": 80,
                "color": "white",
                "stroke_color": "black",
                "stroke_width": 4,
                "font": "Impact",
                "method": "caption",
                "align": "center",
                "bg_color": "rgba(0,0,0,0.5)"
            }
        }
        
        return styles.get(style, styles["modern"])
    
    def prepare_captions_for_video(
        self,
        captions: List[Dict[str, any]],
        style: str = "modern",
        position: str = "bottom"
    ) -> List[Dict[str, any]]:
        """
        Prepare caption data for video rendering.
        
        Args:
            captions: List of caption segments
            style: Caption visual style
            position: Position on screen (top, center, bottom)
        
        Returns:
            Captions with styling information
        """
        style_config = self.get_caption_style_config(style)
        
        # Add position
        position_map = {
            "top": ("center", "top"),
            "center": ("center", "center"),
            "bottom": ("center", "bottom")
        }
        style_config["position"] = position_map.get(position, position_map["bottom"])
        
        # Add style to each caption
        styled_captions = []
        for caption in captions:
            styled_caption = {**caption, **style_config}
            styled_captions.append(styled_caption)
        
        return styled_captions

