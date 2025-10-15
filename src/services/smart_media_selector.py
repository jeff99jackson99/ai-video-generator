"""Smart media selection using GPT-4 to generate perfect Pexels search queries."""

import asyncio
from pathlib import Path
from typing import Dict, List, Optional
import httpx
import json


class SmartMediaSelector:
    """Uses GPT-4 to intelligently select media based on what's being said in the script."""

    def __init__(
        self,
        openai_api_key: Optional[str] = None,
        pexels_key: Optional[str] = None,
        cache_dir: Path = Path("./data/media")
    ):
        """Initialize smart media selector."""
        self.openai_api_key = openai_api_key
        self.pexels_key = pexels_key
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.used_queries = set()  # Track queries to ensure variety

    async def fetch_perfect_media_per_scene(
        self,
        scenes: List[Dict],
        media_fetcher
    ) -> List[tuple[Path, Dict]]:
        """
        Fetch perfect media for each scene using GPT-4 perfect search queries.
        
        Returns:
            List of (media_path, scene_metadata) tuples with playback speed and transition info
        """
        results = []
        
        print(f"🧠 Using GPT-4 to generate PERFECT search queries for {len(scenes)} scenes...")
        
        for i, scene in enumerate(scenes):
            # Generate perfect search query using GPT-4
            search_data = await self.generate_perfect_pexels_query(scene)
            
            # Fetch media using the perfect query
            media_path = await self._fetch_media_with_perfect_query(
                search_data,
                media_fetcher,
                scene_index=i
            )
            
            if media_path:
                # Store metadata with media
                scene_metadata = {
                    'media_type': search_data.get('media_type', 'mixed'),
                    'playback_speed': search_data.get('playback_speed', 1.0),
                    'transition_out': search_data.get('transition_out', 'crossfade'),
                    'search_query': search_data.get('search_query', ''),
                    'reasoning': search_data.get('reasoning', '')
                }
                results.append((media_path, scene_metadata))
                print(f"  ✅ Scene {i+1}: '{search_data['search_query']}' (speed: {search_data['playback_speed']}x, {search_data['media_type']})")
            else:
                print(f"  ⚠️ Scene {i+1}: No media found for '{search_data.get('search_query', 'N/A')}'")
                # Fallback
                fallback = await media_fetcher._create_artistic_placeholders(["placeholder"], 1)
                if fallback:
                    results.append((fallback[0], {
                        'media_type': 'photo',
                        'playback_speed': 1.0,
                        'transition_out': 'crossfade',
                        'search_query': 'fallback',
                        'reasoning': 'fallback placeholder'
                    }))
        
        return results

    async def generate_perfect_pexels_query(self, scene: Dict) -> Dict:
        """
        Use GPT-4 to generate the PERFECT Pexels search query for this exact scene.
        
        Analyzes what's being said and generates search terms that will find
        EXACTLY the right footage - not generic religious imagery!
        """
        if not self.openai_api_key:
            # Fallback to basic keywords
            return {
                'search_query': ' '.join(scene.get('visual_keywords', ['nature'])[:3]),
                'media_type': 'mixed',
                'playback_speed': 1.0,
                'transition_out': 'crossfade',
                'reasoning': 'No OpenAI key - using fallback'
            }

        try:
            narration = scene.get('text', '')
            visual_desc = scene.get('visual_description', '')
            
            prompt = f"""Analyze this video scene narration and generate the PERFECT Pexels search query.

NARRATION: "{narration}"
VISUAL DESCRIPTION: "{visual_desc}"

YOUR TASK: Generate a 3-5 word Pexels search query that will find footage showing EXACTLY what's happening in this moment.

CRITICAL RULES:
1. Focus on ACTIONS and VERBS from narration
   - "extends his hand" → "hand reaching out gesture"
   - "speaking to crowd" → "person speaking audience"
   - NOT generic terms like "forgiveness" or "jesus"

2. Focus on SPECIFIC OBJECTS/SYMBOLS mentioned
   - "open Bible" → "bible book open pages"
   - "sunrise over hills" → "sunrise mountain landscape"
   
3. Focus on EMOTIONS if mentioned
   - "feeling peace" → "peaceful person calm serene"
   - "joy and celebration" → "people celebrating happy joyful"

4. Determine best media type:
   - Use "video" for: actions, movement, people doing things
   - Use "photo" for: static objects, landscapes, symbolic imagery
   
5. Determine playback speed:
   - 0.5-0.7: Slow motion for dramatic, peaceful, contemplative moments
   - 1.0: Normal for standard narration
   - 1.2-1.5: Faster for exciting, energetic, action moments
   
6. Determine transition type:
   - "crossfade": Smooth, peaceful transitions
   - "zoom": Emphasis, drawing attention
   - "quick_cut": Fast-paced, exciting content
   - "fade_black": Dramatic pause between major ideas

7. ENSURE VARIETY: Never use the same search twice

RESPOND IN THIS EXACT JSON FORMAT:
{{
    "search_query": "3-5 word perfect query",
    "media_type": "video" or "photo",
    "playback_speed": 1.0,
    "transition_out": "crossfade" or "zoom" or "quick_cut" or "fade_black",
    "reasoning": "Brief explanation of why this query/settings"
}}"""

            async with httpx.AsyncClient(timeout=20.0) as client:
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
                                "content": "You are an expert at creating perfect Pexels search queries. Return only valid JSON."
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        "temperature": 0.8,  # Creativity for variety
                        "max_tokens": 200,
                        "response_format": {"type": "json_object"}
                    }
                )
                response.raise_for_status()
                data = response.json()
                
                content = data['choices'][0]['message']['content']
                result = json.loads(content)
                
                # Ensure variety - if query was used, modify it slightly
                query = result.get('search_query', 'nature')
                if query in self.used_queries:
                    query = query + " closeup"  # Slight variation
                self.used_queries.add(query)
                result['search_query'] = query
                
                return result

        except Exception as e:
            print(f"⚠️ GPT-4 query generation error: {e}")
            # Fallback
            return {
                'search_query': ' '.join(scene.get('visual_keywords', ['peaceful nature'])[:3]),
                'media_type': 'mixed',
                'playback_speed': 1.0,
                'transition_out': 'crossfade',
                'reasoning': f'Fallback due to error: {str(e)}'
            }

    async def _fetch_media_with_perfect_query(
        self,
        search_data: Dict,
        media_fetcher,
        scene_index: int
    ) -> Optional[Path]:
        """Fetch media using the perfect query."""
        query = search_data.get('search_query', 'nature')
        media_type = search_data.get('media_type', 'mixed')
        
        try:
            if media_fetcher.pexels_key:
                # Search Pexels with perfect query
                fetch_type = media_type if media_type in ['photos', 'videos'] else (
                    "photos" if scene_index % 2 == 0 else "videos"
                )
                
                media_urls = await media_fetcher._search_pexels(
                    [query],
                    count=1,
                    media_type=fetch_type
                )
                
                if media_urls:
                    media_path = await media_fetcher._download_file(media_urls[0])
                    return media_path
            
            # Fallback to Unsplash
            if media_type in ["photos", "mixed"]:
                keyword = query.replace(' ', ',')
                url = f"https://source.unsplash.com/1920x1080/?{keyword}"
                media_path = await media_fetcher._download_file_with_fallback(url, query, scene_index)
                return media_path
                
        except Exception as e:
            print(f"Error fetching with perfect query '{query}': {e}")
        
        return None

