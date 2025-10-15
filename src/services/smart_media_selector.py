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

LEARN FROM THESE PROVEN EXAMPLES:

EXAMPLE 1:
Script: "smiling in photos, but inside, you feel hollow"
✅ PERFECT: "person smiling feeling empty"
❌ WRONG: "happiness" (too generic)
Speed: 1.0x | Type: video | Transition: crossfade

EXAMPLE 2:
Script: "scrolling, laugh, act like everything's fine"
✅ PERFECT: "person scrolling laughing phone"
❌ WRONG: "social media" (not specific enough)
Speed: 1.0x | Type: video | Transition: quick_cut

EXAMPLE 3:
Script: "Something deep inside you knows"
✅ PERFECT: "inner knowing person reflection"
❌ WRONG: "thinking" (not emotional enough)
Speed: 0.7x SLOW | Type: video | Transition: crossfade

EXAMPLE 4:
Script: "He never stopped reaching for you"
✅ PERFECT: "hand reaching out gesture"
❌ WRONG: "god reaching" (use physical action, not concept)
Speed: 1.0x | Type: video | Transition: zoom

EXAMPLE 5:
Script: "He chose the cross for you"
✅ PERFECT: "man bearing cross sacrifice"
❌ WRONG: "crucifixion" (too graphic)
Speed: 1.0x | Type: video | Transition: fade_black

EXAMPLE 6:
Script: "take the weight off your shoulders"
✅ PERFECT: "person releasing burdens gesture"
❌ WRONG: "relief" (use physical action)
Speed: 0.7x SLOW | Type: video | Transition: crossfade

EXAMPLE 7:
Script: "calling your name"
✅ PERFECT: "hands reaching out gesture"
❌ WRONG: "prayer" (too generic)
Speed: 1.0x | Type: video | Transition: crossfade

EXAMPLE 8:
Script: "walking through the storm"
✅ PERFECT: "person walking rain storm"
❌ WRONG: "difficulty" (use literal imagery)
Speed: 1.2x FAST | Type: video | Transition: quick_cut

EXAMPLE 9:
Script: "open Bible on the table"
✅ PERFECT: "bible book open pages closeup"
❌ WRONG: "scripture" (use specific object)
Speed: 1.0x | Type: photo | Transition: crossfade

EXAMPLE 10:
Script: "sunrise breaking through darkness"
✅ PERFECT: "sunrise dawn breaking clouds"
❌ WRONG: "hope" (use literal visual)
Speed: 0.8x SLOW | Type: video | Transition: crossfade

EXAMPLE 11:
Script: "running into His arms"
✅ PERFECT: "person running open arms embrace"
❌ WRONG: "reunion" (use action)
Speed: 1.3x FAST | Type: video | Transition: quick_cut

EXAMPLE 12:
Script: "tears streaming down her face"
✅ PERFECT: "woman crying tears closeup face"
❌ WRONG: "sadness" (use specific visual)
Speed: 0.6x SLOW | Type: video | Transition: crossfade

EXAMPLE 13:
Script: "kneeling in prayer"
✅ PERFECT: "person kneeling praying hands"
❌ WRONG: "worship" (use physical position)
Speed: 0.8x SLOW | Type: video | Transition: fade_black

EXAMPLE 14:
Script: "celebrating with joyful dancing"
✅ PERFECT: "people dancing celebration happy"
❌ WRONG: "joy" (use action)
Speed: 1.4x FAST | Type: video | Transition: quick_cut

EXAMPLE 15:
Script: "looking up to heaven"
✅ PERFECT: "person looking up sky clouds"
❌ WRONG: "heaven" (use physical action)
Speed: 1.0x | Type: video | Transition: zoom

EXAMPLE 16:
Script: "broken chains falling to the ground"
✅ PERFECT: "chains breaking falling freedom"
❌ WRONG: "freedom" (use literal chains)
Speed: 1.2x FAST | Type: video | Transition: quick_cut

EXAMPLE 17:
Script: "sitting alone in the dark"
✅ PERFECT: "person sitting alone darkness room"
❌ WRONG: "loneliness" (use physical scene)
Speed: 0.7x SLOW | Type: video | Transition: fade_black

EXAMPLE 18:
Script: "children playing and laughing"
✅ PERFECT: "children playing laughing happy joyful"
❌ WRONG: "innocence" (use action)
Speed: 1.3x FAST | Type: video | Transition: quick_cut

EXAMPLE 19:
Script: "holding hands together in unity"
✅ PERFECT: "hands holding together unity closeup"
❌ WRONG: "togetherness" (use physical touch)
Speed: 1.0x | Type: video | Transition: crossfade

EXAMPLE 20:
Script: "ocean waves crashing on shore"
✅ PERFECT: "ocean waves crashing beach shore"
❌ WRONG: "nature" (use specific imagery)
Speed: 1.0x | Type: video | Transition: crossfade

EXAMPLE 21:
Script: "heart beating with new life"
✅ PERFECT: "heartbeat pulse life closeup"
❌ WRONG: "life" (use specific visual)
Speed: 1.1x FAST | Type: video | Transition: zoom

EXAMPLE 22:
Script: "whispering a quiet prayer"
✅ PERFECT: "person whispering quiet prayer closeup"
❌ WRONG: "meditation" (use specific action)
Speed: 0.8x SLOW | Type: video | Transition: crossfade

EXAMPLE 23:
Script: "standing at the crossroads"
✅ PERFECT: "person standing crossroads road path"
❌ WRONG: "decision" (use literal crossroads)
Speed: 1.0x | Type: video | Transition: fade_black

EXAMPLE 24:
Script: "mountains towering in the distance"
✅ PERFECT: "mountains towering landscape distance"
❌ WRONG: "strength" (use literal mountains)
Speed: 0.9x SLOW | Type: video | Transition: crossfade

EXAMPLE 25:
Script: "fire burning brightly"
✅ PERFECT: "fire flames burning bright closeup"
❌ WRONG: "passion" (use literal fire)
Speed: 1.2x FAST | Type: video | Transition: zoom

EXAMPLE 26:
Script: "embracing loved ones tightly"
✅ PERFECT: "people embracing hugging tight love"
❌ WRONG: "love" (use physical embrace)
Speed: 0.8x SLOW | Type: video | Transition: crossfade

EXAMPLE 27:
Script: "walking confidently forward"
✅ PERFECT: "person walking confident forward path"
❌ WRONG: "confidence" (use action)
Speed: 1.1x FAST | Type: video | Transition: quick_cut

EXAMPLE 28:
Script: "closing eyes in peace"
✅ PERFECT: "person closing eyes peaceful calm"
❌ WRONG: "peace" (use action)
Speed: 0.7x SLOW | Type: video | Transition: crossfade

EXAMPLE 29:
Script: "hands lifted in worship"
✅ PERFECT: "hands raised lifted worship gesture"
❌ WRONG: "praise" (use physical gesture)
Speed: 0.9x SLOW | Type: video | Transition: zoom

EXAMPLE 30:
Script: "breaking through the clouds"
✅ PERFECT: "light breaking through clouds sky"
❌ WRONG: "breakthrough" (use literal visual)
Speed: 1.0x | Type: video | Transition: zoom

EXAMPLE 31:
Script: "carrying heavy burden uphill"
✅ PERFECT: "person carrying weight uphill struggle"
❌ WRONG: "burden" (use physical carrying)
Speed: 0.9x SLOW | Type: video | Transition: crossfade

EXAMPLE 32:
Script: "door opening to light"
✅ PERFECT: "door opening light shining through"
❌ WRONG: "opportunity" (use literal door)
Speed: 1.0x | Type: video | Transition: zoom

EXAMPLE 33:
Script: "flowers blooming in spring"
✅ PERFECT: "flowers blooming spring garden closeup"
❌ WRONG: "renewal" (use literal flowers)
Speed: 0.8x SLOW | Type: video | Transition: crossfade

EXAMPLE 34:
Script: "running from darkness to light"
✅ PERFECT: "person running darkness light"
❌ WRONG: "transformation" (use action)
Speed: 1.3x FAST | Type: video | Transition: quick_cut

EXAMPLE 35:
Script: "falling to knees in surrender"
✅ PERFECT: "person falling knees surrender"
❌ WRONG: "submission" (use action)
Speed: 0.7x SLOW | Type: video | Transition: fade_black

EXAMPLE 36:
Script: "shouting with joy and victory"
✅ PERFECT: "person shouting joy celebration victory"
❌ WRONG: "triumph" (use action)
Speed: 1.4x FAST | Type: video | Transition: quick_cut

EXAMPLE 37:
Script: "gentle rain falling softly"
✅ PERFECT: "rain falling soft gentle drops"
❌ WRONG: "blessing" (use literal rain)
Speed: 0.8x SLOW | Type: video | Transition: crossfade

EXAMPLE 38:
Script: "throwing off old garments"
✅ PERFECT: "person removing clothes throwing off"
❌ WRONG: "change" (use physical action)
Speed: 1.2x FAST | Type: video | Transition: quick_cut

EXAMPLE 39:
Script: "footsteps walking on path"
✅ PERFECT: "feet walking path closeup steps"
❌ WRONG: "journey" (use literal feet)
Speed: 1.0x | Type: video | Transition: crossfade

EXAMPLE 40:
Script: "candle flame flickering"
✅ PERFECT: "candle flame flickering light closeup"
❌ WRONG: "hope" (use literal candle)
Speed: 0.9x SLOW | Type: video | Transition: crossfade

EXAMPLE 41:
Script: "jumping for joy"
✅ PERFECT: "person jumping happy joy celebration"
❌ WRONG: "happiness" (use jumping action)
Speed: 1.3x FAST | Type: video | Transition: quick_cut

EXAMPLE 42:
Script: "blood dripping from wounds"
✅ PERFECT: "water drops red sacrifice closeup"
❌ WRONG: "sacrifice" (use tasteful alternative)
Speed: 0.6x SLOW | Type: video | Transition: fade_black

EXAMPLE 43:
Script: "crown placed on head"
✅ PERFECT: "crown placing head royalty gesture"
❌ WRONG: "kingship" (use physical action)
Speed: 0.8x SLOW | Type: video | Transition: zoom

EXAMPLE 44:
Script: "seeds planted in soil"
✅ PERFECT: "seeds planting soil hands garden"
❌ WRONG: "growth" (use literal planting)
Speed: 1.0x | Type: video | Transition: crossfade

EXAMPLE 45:
Script: "shadows fleeing from light"
✅ PERFECT: "shadows disappearing light bright"
❌ WRONG: "victory" (use literal shadow/light)
Speed: 1.1x FAST | Type: video | Transition: zoom

EXAMPLE 46:
Script: "writing on scroll"
✅ PERFECT: "hand writing scroll pen closeup"
❌ WRONG: "scripture" (use writing action)
Speed: 1.0x | Type: video | Transition: crossfade

EXAMPLE 47:
Script: "stars shining in night sky"
✅ PERFECT: "stars shining night sky galaxy"
❌ WRONG: "guidance" (use literal stars)
Speed: 0.9x SLOW | Type: video | Transition: crossfade

EXAMPLE 48:
Script: "breaking bread together"
✅ PERFECT: "hands breaking bread sharing meal"
❌ WRONG: "communion" (use physical action)
Speed: 0.8x SLOW | Type: video | Transition: crossfade

EXAMPLE 49:
Script: "water flowing from rock"
✅ PERFECT: "water flowing rock stream spring"
❌ WRONG: "provision" (use literal water)
Speed: 1.0x | Type: video | Transition: crossfade

EXAMPLE 50:
Script: "trumpet sounding loudly"
✅ PERFECT: "trumpet sound music loud celebration"
❌ WRONG: "announcement" (use literal trumpet)
Speed: 1.2x FAST | Type: video | Transition: quick_cut

CRITICAL RULES:
1. Focus on PHYSICAL ACTIONS & VERBS (reaching, walking, crying, smiling, kneeling)
2. Use SPECIFIC OBJECTS when mentioned (hand, face, cross, bible, phone)
3. Include EMOTIONS with actions ("smiling feeling empty", "crying tears")
4. AVOID abstract concepts (forgiveness, hope, heaven) - use CONCRETE visuals
5. AVOID religious figure names - use actions/symbols instead
6. Keep queries 3-5 words MAX
7. Determine best media type:
   - "video" for: actions, movement, people doing things
   - "photo" for: static objects only
8. Determine playback speed:
   - 0.5-0.7: Slow motion (dramatic, peaceful, contemplative, emotional)
   - 1.0: Normal (standard narration)
   - 1.2-1.5: Fast (exciting, energetic, action, celebration)
9. Determine transition:
   - "crossfade": Smooth, peaceful, standard
   - "zoom": Emphasis, important moments
   - "quick_cut": Fast-paced, exciting, energetic
   - "fade_black": Dramatic pause, major topic shift
10. ENSURE VARIETY: Never repeat searches

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
