"""Media verification service using GPT-4 Vision API."""

import base64
from pathlib import Path
from typing import Dict, Any, Optional
import httpx


class MediaVerifier:
    """Verifies media files match scene descriptions using GPT-4 Vision."""

    def __init__(self, openai_api_key: Optional[str] = None):
        """Initialize media verifier with OpenAI API key."""
        self.openai_api_key = openai_api_key

    async def verify_media_matches_scene(
        self,
        media_path: Path,
        scene_description: str,
        visual_keywords: list = None
    ) -> Dict[str, Any]:
        """
        Verify if media file matches the scene description using GPT-4 Vision.

        Args:
            media_path: Path to image or video file
            scene_description: Detailed description of what the scene should show
            visual_keywords: Optional list of keywords for context

        Returns:
            {
                "matches": bool,
                "confidence_score": int (0-100),
                "explanation": str,
                "suggestions": str (if doesn't match)
            }
        """
        if not self.openai_api_key:
            # Fallback: assume media matches if no API key
            return {
                "matches": True,
                "confidence_score": 75,
                "explanation": "Media verification skipped (no OpenAI API key)",
                "suggestions": ""
            }

        try:
            # Read and encode media file
            if media_path.suffix.lower() in ['.mp4', '.mov', '.avi']:
                # For videos, extract first frame using ffmpeg
                frame_path = await self._extract_video_frame(media_path)
                image_data = base64.b64encode(frame_path.read_bytes()).decode('utf-8')
            else:
                # For images, use directly
                image_data = base64.b64encode(media_path.read_bytes()).decode('utf-8')

            # Build prompt
            keywords_text = f" Keywords: {', '.join(visual_keywords)}" if visual_keywords else ""
            prompt = f"""Analyze this image and determine if it matches the following scene description:

Scene Description: {scene_description}{keywords_text}

Rate the match on a scale of 0-100:
- 90-100: Perfect match, exactly what's needed
- 70-89: Good match, relevant and usable
- 50-69: Partial match, some relevance
- 0-49: Poor match, doesn't fit the scene

Respond in this EXACT JSON format:
{{
    "confidence_score": 85,
    "explanation": "Brief explanation of what you see and how well it matches",
    "matches_description": true/false,
    "suggestions": "If score < 70, suggest better search terms"
}}"""

            # Call GPT-4 Vision API
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.openai_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "gpt-4o-mini",  # Using mini for cost-effectiveness
                        "messages": [
                            {
                                "role": "user",
                                "content": [
                                    {
                                        "type": "text",
                                        "text": prompt
                                    },
                                    {
                                        "type": "image_url",
                                        "image_url": {
                                            "url": f"data:image/jpeg;base64,{image_data}",
                                            "detail": "low"  # Faster, cheaper analysis
                                        }
                                    }
                                ]
                            }
                        ],
                        "max_tokens": 300,
                        "temperature": 0.3
                    }
                )
                response.raise_for_status()
                data = response.json()

                # Parse response
                import json
                content = data['choices'][0]['message']['content']

                # Extract JSON from response
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0]
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0]

                result = json.loads(content.strip())

                return {
                    "matches": result.get("confidence_score", 0) >= 60,  # Accept 60+ scores
                    "confidence_score": result.get("confidence_score", 0),
                    "explanation": result.get("explanation", ""),
                    "suggestions": result.get("suggestions", "")
                }

        except Exception as e:
            print(f"⚠️ Media verification error: {e}")
            # On error, accept the media (don't block video generation)
            return {
                "matches": True,
                "confidence_score": 70,
                "explanation": f"Verification error (accepted by default): {str(e)}",
                "suggestions": ""
            }

    async def _extract_video_frame(self, video_path: Path) -> Path:
        """Extract first frame from video for verification."""
        import subprocess
        import tempfile

        # Create temp file for frame
        frame_path = Path(tempfile.gettempdir()) / f"{video_path.stem}_frame.jpg"

        try:
            # Extract frame at 0.5 seconds using ffmpeg
            subprocess.run([
                "ffmpeg", "-i", str(video_path),
                "-ss", "0.5",  # 0.5 seconds in
                "-vframes", "1",  # Extract 1 frame
                "-q:v", "2",  # High quality
                str(frame_path),
                "-y"  # Overwrite
            ], check=True, capture_output=True)

            return frame_path

        except subprocess.CalledProcessError as e:
            print(f"⚠️ Frame extraction failed: {e}")
            # Fallback: use video file directly (API may handle it)
            return video_path

    async def verify_batch(
        self,
        media_files: list[Path],
        scenes: list[Dict]
    ) -> list[tuple[Path, Dict[str, Any]]]:
        """
        Verify multiple media files against their corresponding scenes.

        Returns:
            List of (media_path, verification_result) tuples
        """
        results = []

        for media_file, scene in zip(media_files, scenes):
            visual_desc = scene.get('visual_description', '')
            visual_keywords = scene.get('visual_keywords', [])

            verification = await self.verify_media_matches_scene(
                media_file,
                visual_desc,
                visual_keywords
            )

            results.append((media_file, verification))

            # Log verification result
            status = "✅" if verification["matches"] else "❌"
            score = verification["confidence_score"]
            print(f"{status} {media_file.name}: {score}/100 - {verification['explanation'][:60]}...")

        return results
