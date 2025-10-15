"""AI script enhancement service using free/open-source models."""

import os
from typing import Optional, Dict, Any, List
import httpx


class ScriptEnhancer:
    """Enhances scripts using AI models."""

    def __init__(
        self,
        openai_api_key: Optional[str] = None,
        gemini_api_key: Optional[str] = None,
        groq_api_key: Optional[str] = None
    ):
        """Initialize script enhancer."""
        self.openai_api_key = openai_api_key
        self.gemini_api_key = gemini_api_key
        self.groq_api_key = groq_api_key

    async def enhance_script(self, script: str) -> Dict[str, Any]:
        """
        Enhance script with AI - tries best models first.

        Priority: OpenAI GPT-4 > Gemini > Groq > Basic

        Returns:
            {
                "enhanced_script": str,
                "scenes": List[Dict],
                "keywords": List[str],
                "mood": str,
                "duration_estimate": int
            }
        """
        # Try OpenAI GPT-4 first (best quality) if API key is available
        if self.openai_api_key:
            try:
                print("🤖 Using OpenAI GPT-4 for script enhancement...")
                return await self._enhance_with_openai(script)
            except Exception as e:
                print(f"OpenAI API error: {e}, falling back to Gemini")

        # Try Gemini as second choice
        if self.gemini_api_key:
            try:
                print("🤖 Using Google Gemini for script enhancement...")
                return await self._enhance_with_gemini(script)
            except Exception as e:
                print(f"Gemini API error: {e}, falling back to Groq")

        # Try Groq as third choice (fast and free)
        if self.groq_api_key:
            try:
                print("🤖 Using Groq for script enhancement...")
                return await self._enhance_with_groq(script)
            except Exception as e:
                print(f"Groq API error: {e}, using basic enhancement")

        # Basic enhancement without AI (fallback)
        print("ℹ️ Using basic enhancement (no API keys configured)")
        return self._basic_enhancement(script)

    async def _enhance_with_openai(self, script: str) -> Dict[str, Any]:
        """Enhance script using OpenAI GPT-4 (best quality)."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.openai_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-4o-mini",  # Fast and cost-effective GPT-4
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a professional video script writer and content strategist. You enhance scripts to be more engaging, visual, and impactful. Return responses in valid JSON format only."
                        },
                        {
                            "role": "user",
                            "content": f"""Analyze and enhance this video script:

{script}

Provide a comprehensive analysis in this EXACT JSON format:
{{
    "enhanced_script": "An improved, more engaging version with better pacing and clarity",
    "scenes": [
        {{
            "text": "Scene narration text",
            "visual_description": "Detailed description of what visuals to show",
            "duration": 5
        }}
    ],
    "keywords": ["keyword1", "keyword2", "keyword3"],
    "mood": "inspirational/professional/upbeat/calm/dramatic/educational",
    "duration_estimate": 90
}}

Make the enhanced script more impactful and visual. Break it into well-paced scenes. Extract specific visual keywords that would make great imagery."""
                        }
                    ],
                    "temperature": 0.7,
                    "max_tokens": 2000,
                    "response_format": {"type": "json_object"}
                },
                timeout=30.0
            )
            response.raise_for_status()
            data = response.json()

            import json
            content = data['choices'][0]['message']['content']
            result = json.loads(content)

            print(f"✅ OpenAI GPT-4 enhanced script successfully!")
            return result

    async def _enhance_with_gemini(self, script: str) -> Dict[str, Any]:
        """Enhance script using Google Gemini API."""
        try:
            import google.generativeai as genai

            genai.configure(api_key=self.gemini_api_key)
            model = genai.GenerativeModel('gemini-pro')

            prompt = f"""Analyze this video script and provide:
1. An enhanced version with better pacing and clarity
2. Break it into scenes with visual descriptions
3. Extract 5-10 keywords for finding relevant images/videos
4. Determine the overall mood/tone (e.g., professional, inspirational, educational)
5. Estimate duration in seconds

Script:
{script}

Return your response in this JSON format:
{{
    "enhanced_script": "improved script here",
    "scenes": [
        {{"text": "scene text", "visual_description": "what to show", "duration": 5}},
        ...
    ],
    "keywords": ["keyword1", "keyword2", ...],
    "mood": "mood description",
    "duration_estimate": 60
}}"""

            response = model.generate_content(prompt)

            # Parse JSON from response
            import json
            # Extract JSON from markdown code blocks if present
            text = response.text.strip()
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]

            return json.loads(text)

        except Exception as e:
            raise Exception(f"Gemini API error: {e}")

    async def _enhance_with_groq(self, script: str) -> Dict[str, Any]:
        """Enhance script using Groq API."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.groq_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "mixtral-8x7b-32768",
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a video script enhancement AI. Return valid JSON only."
                        },
                        {
                            "role": "user",
                            "content": f"""Analyze this video script and provide a JSON response with:
1. Enhanced script with better pacing
2. Scenes with visual descriptions
3. Keywords for finding media
4. Mood/tone
5. Duration estimate

Script: {script}

Return ONLY valid JSON in this format:
{{"enhanced_script": "...", "scenes": [{{"text": "...", "visual_description": "...", "duration": 5}}], "keywords": ["..."], "mood": "...", "duration_estimate": 60}}"""
                        }
                    ],
                    "temperature": 0.7,
                    "max_tokens": 2000
                }
            )
            response.raise_for_status()
            data = response.json()

            import json
            content = data['choices'][0]['message']['content']
            # Clean markdown if present
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]

            return json.loads(content)

    def _basic_enhancement(self, script: str) -> Dict[str, Any]:
        """Basic script enhancement without AI."""
        # Split script into sentences
        import re
        sentences = re.split(r'[.!?]+', script)
        sentences = [s.strip() for s in sentences if s.strip()]

        # Create basic scenes (one or two sentences per scene)
        # Make scenes longer for better viewing
        scenes = []
        for i in range(0, len(sentences), 2):
            scene_text = ". ".join(sentences[i:i+2]) + "."
            # Calculate duration based on text length (reading pace: ~3 words/second)
            word_count = len(scene_text.split())
            duration = max(6, min(12, word_count / 2.5))  # 6-12 seconds per scene
            
            scenes.append({
                "text": scene_text,
                "visual_description": f"Visual for: {scene_text[:50]}...",
                "duration": duration
            })

        # Extract simple keywords (nouns and important words)
        words = script.lower().split()
        # Filter out common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were'}
        keywords = list(set([w.strip('.,!?') for w in words if len(w) > 4 and w not in stop_words]))[:10]

        return {
            "enhanced_script": script,
            "scenes": scenes,
            "keywords": keywords,
            "mood": "professional",
            "duration_estimate": len(scenes) * 5
        }

    def extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text for media search."""
        # Simple keyword extraction
        words = text.lower().split()
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were'}
        keywords = [w.strip('.,!?') for w in words if len(w) > 3 and w not in stop_words]
        return list(set(keywords))[:10]
