"""AI-powered video quality enhancement and review system."""

from pathlib import Path
from typing import Optional, Dict, Any
import httpx


class VideoQualityEnhancer:
    """Uses AI to review and enhance video quality."""

    def __init__(self, openai_api_key: Optional[str] = None):
        """Initialize quality enhancer."""
        self.openai_api_key = openai_api_key

    async def analyze_video_quality(
        self,
        video_path: Path,
        script: str,
        scenes: list,
        keywords: list
    ) -> Dict[str, Any]:
        """
        Use AI to analyze video quality and suggest improvements.

        Returns suggestions for the next generation iteration.
        """
        if not self.openai_api_key:
            return {"suggestions": [], "quality_score": 7}

        try:
            # Create analysis prompt
            analysis_prompt = f"""Analyze this video generation and suggest improvements:

Original Script:
{script}

Scenes Generated: {len(scenes)}
Keywords Used: {', '.join(keywords[:10])}
Duration: {sum(s.get('duration', 5) for s in scenes)} seconds

Review the video generation parameters and suggest:
1. Better visual keywords for more relevant images
2. Improved scene timing and pacing
3. Better mood/tone for background music
4. Caption style recommendations
5. Overall quality improvements

Return JSON:
{{
    "quality_score": 8,
    "improved_keywords": ["keyword1", "keyword2"],
    "scene_pacing_suggestions": "Make scene 1 longer for impact...",
    "visual_improvements": "Use more specific spiritual imagery...",
    "mood_recommendation": "inspirational",
    "caption_style": "bold",
    "next_iteration_tips": "Focus on...",
    "overall_assessment": "Good start, but..."
}}"""

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.openai_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "gpt-4o-mini",
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are a professional video quality analyst. Provide constructive feedback to improve video generation."
                            },
                            {
                                "role": "user",
                                "content": analysis_prompt
                            }
                        ],
                        "temperature": 0.7,
                        "max_tokens": 1000,
                        "response_format": {"type": "json_object"}
                    },
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()

                import json
                analysis = json.loads(data['choices'][0]['message']['content'])

                print(f"🎯 AI Quality Analysis Complete! Score: {analysis.get('quality_score', 0)}/10")
                return analysis

        except Exception as e:
            print(f"Quality analysis error: {e}")
            return {"suggestions": [], "quality_score": 7}

    def should_regenerate(self, analysis: Dict[str, Any], threshold: int = 7) -> bool:
        """Determine if video should be regenerated based on quality score."""
        score = analysis.get('quality_score', 10)
        return score < threshold

    def apply_improvements(
        self,
        original_script: str,
        original_scenes: list,
        analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Apply AI suggestions to improve next generation.

        Returns enhanced parameters for regeneration.
        """
        improvements = {
            "keywords": analysis.get('improved_keywords', []),
            "mood": analysis.get('mood_recommendation', 'professional'),
            "caption_style": analysis.get('caption_style', 'modern'),
            "suggestions": analysis.get('next_iteration_tips', '')
        }

        return improvements
