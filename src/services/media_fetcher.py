"""Media fetcher service for downloading free stock photos and videos."""

import asyncio
import hashlib
from pathlib import Path
from typing import List, Dict, Optional, Any
import httpx
from PIL import Image


class MediaFetcher:
    """Fetches free stock media from various sources."""

    def __init__(
        self,
        pexels_key: Optional[str] = None,
        unsplash_key: Optional[str] = None,
        pixabay_key: Optional[str] = None,
        cache_dir: Path = Path("./data/media")
    ):
        """Initialize media fetcher."""
        self.pexels_key = pexels_key
        self.unsplash_key = unsplash_key
        self.pixabay_key = pixabay_key
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    async def search_and_download(
        self,
        keywords: List[str],
        count: int = 5,
        media_type: str = "mixed"  # "photos", "videos", or "mixed"
    ) -> List[Path]:
        """
        Search for and download media based on keywords.

        Args:
            keywords: List of search keywords
            count: Number of media files to fetch
            media_type: "photos", "videos", or "mixed" (mix of both)

        Returns:
            List of downloaded media file paths
        """
        all_media = []

        # For mixed, get both photos and short video clips
        if media_type == "mixed" and self.pexels_key:
            # Get mix: 60% photos, 40% videos for dynamic content
            photo_count = int(count * 0.6) or 1
            video_count = count - photo_count

            print(f"📸 Fetching {photo_count} photos and 🎥 {video_count} video clips from Pexels...")

            tasks = [
                self._search_pexels(keywords, photo_count, "photos"),
                self._search_pexels(keywords, video_count, "videos")
            ]

            results = await asyncio.gather(*tasks, return_exceptions=True)
            for result in results:
                if isinstance(result, list):
                    all_media.extend(result)

        else:
            # Regular single-type search
            tasks = []
            if self.pexels_key:
                tasks.append(self._search_pexels(keywords, count, media_type))
            if self.unsplash_key and media_type == "photos":
                tasks.append(self._search_unsplash(keywords, count))
            if self.pixabay_key:
                tasks.append(self._search_pixabay(keywords, count, media_type))

            if not tasks:
                # No API keys, use fallback
                return await self._fallback_media(keywords, count, media_type)

            results = await asyncio.gather(*tasks, return_exceptions=True)

            for result in results:
                if isinstance(result, list):
                    all_media.extend(result)

        # Download media files
        downloaded = []
        for media_url in all_media[:count * 2]:  # Get extra in case some fail
            try:
                file_path = await self._download_file(media_url)
                if file_path:
                    downloaded.append(file_path)
                    if len(downloaded) >= count:
                        break
            except Exception as e:
                print(f"Error downloading {media_url}: {e}")

        print(f"✅ Downloaded {len(downloaded)} media files (mix of photos and videos)")
        return downloaded

    async def _search_pexels(
        self,
        keywords: List[str],
        count: int,
        media_type: str
    ) -> List[str]:
        """Search Pexels API."""
        query = " ".join(keywords[:3])

        async with httpx.AsyncClient() as client:
            if media_type == "photos":
                url = "https://api.pexels.com/v1/search"
            else:
                url = "https://api.pexels.com/videos/search"

            response = await client.get(
                url,
                headers={"Authorization": self.pexels_key},
                params={"query": query, "per_page": count}
            )
            response.raise_for_status()
            data = response.json()

            urls = []
            if media_type == "photos":
                for photo in data.get("photos", []):
                    urls.append(photo["src"]["large"])
            else:
                for video in data.get("videos", []):
                    if video.get("video_files"):
                        # Get HD file
                        urls.append(video["video_files"][0]["link"])

            return urls

    async def _search_unsplash(
        self,
        keywords: List[str],
        count: int
    ) -> List[str]:
        """Search Unsplash API."""
        query = " ".join(keywords[:3])

        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.unsplash.com/search/photos",
                headers={"Authorization": f"Client-ID {self.unsplash_key}"},
                params={"query": query, "per_page": count}
            )
            response.raise_for_status()
            data = response.json()

            urls = []
            for photo in data.get("results", []):
                urls.append(photo["urls"]["regular"])

            return urls

    async def _search_pixabay(
        self,
        keywords: List[str],
        count: int,
        media_type: str
    ) -> List[str]:
        """Search Pixabay API."""
        query = " ".join(keywords[:3])

        async with httpx.AsyncClient() as client:
            if media_type == "photos":
                endpoint = "https://pixabay.com/api/"
            else:
                endpoint = "https://pixabay.com/api/videos/"

            response = await client.get(
                endpoint,
                params={
                    "key": self.pixabay_key,
                    "q": query,
                    "per_page": count,
                    "safesearch": "true"
                }
            )
            response.raise_for_status()
            data = response.json()

            urls = []
            if media_type == "photos":
                for item in data.get("hits", []):
                    urls.append(item["largeImageURL"])
            else:
                for item in data.get("hits", []):
                    if item.get("videos", {}).get("medium"):
                        urls.append(item["videos"]["medium"]["url"])

            return urls

    async def _fallback_media(
        self,
        keywords: List[str],
        count: int,
        media_type: str
    ) -> List[Path]:
        """
        Fetch media from free sources without requiring API keys.
        Uses Unsplash Source and Lorem Picsum for free images.
        """
        media_files = []

        if media_type == "photos":
            # Use Unsplash Source (no API key required!)
            # https://source.unsplash.com/1920x1080/?keyword
            print(f"📸 Fetching FREE images from Unsplash Source...")

            for i, keyword in enumerate(keywords[:count]):
                try:
                    # Clean keyword for URL
                    clean_keyword = keyword.lower().replace(' ', ',')

                    # Unsplash Source provides free random images
                    url = f"https://source.unsplash.com/1920x1080/?{clean_keyword}"

                    # Download the image
                    file_path = await self._download_file_with_fallback(url, keyword, i)
                    if file_path:
                        media_files.append(file_path)
                        print(f"✅ Downloaded image for '{keyword}'")
                except Exception as e:
                    print(f"Error fetching image for '{keyword}': {e}")

            # If we got no images, use better placeholders
            if not media_files:
                print("⚠️ No images fetched, creating artistic placeholders...")
                media_files = await self._create_artistic_placeholders(keywords, count)

        return media_files

    async def _download_file_with_fallback(
        self,
        url: str,
        keyword: str,
        index: int
    ) -> Optional[Path]:
        """Download file with proper error handling."""
        import hashlib

        url_hash = hashlib.md5(f"{url}_{index}".encode()).hexdigest()
        file_path = self.cache_dir / f"{keyword[:20]}_{url_hash}.jpg"

        # Return if cached
        if file_path.exists():
            return file_path

        try:
            async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
                response = await client.get(url)
                response.raise_for_status()

                if len(response.content) > 10000:  # Valid image should be > 10KB
                    file_path.write_bytes(response.content)
                    return file_path
        except Exception as e:
            print(f"Download failed for {keyword}: {e}")

        return None

    async def _create_artistic_placeholders(
        self,
        keywords: List[str],
        count: int
    ) -> List[Path]:
        """Create better-looking gradient placeholder images."""
        placeholders = []

        for i, keyword in enumerate(keywords[:count]):
            file_path = self.cache_dir / f"placeholder_{keyword[:20]}_{i}.jpg"

            if not file_path.exists():
                # Create gradient image instead of solid color
                from PIL import ImageDraw, ImageFont
                img = Image.new('RGB', (1920, 1080), color=(40, 40, 50))
                draw = ImageDraw.Draw(img)

                # Add gradient effect
                for y in range(1080):
                    color = (
                        40 + int((i * 30 + y * 0.1) % 100),
                        40 + int((i * 50 + y * 0.15) % 120),
                        50 + int((i * 70 + y * 0.2) % 150)
                    )
                    draw.rectangle([(0, y), (1920, y + 1)], fill=color)

                # Add keyword text
                try:
                    font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 80)
                except:
                    font = None

                text = keyword.upper()[:30]
                draw.text((960, 540), text, fill=(255, 255, 255), font=font, anchor="mm")

                img.save(file_path, 'JPEG', quality=95)

            placeholders.append(file_path)

        return placeholders

    async def _download_file(self, url: str) -> Optional[Path]:
        """Download a file from URL."""
        # Create filename from URL hash
        url_hash = hashlib.md5(url.encode()).hexdigest()

        # Determine extension
        ext = ".jpg"
        if url.endswith((".mp4", ".mov")):
            ext = ".mp4"
        elif url.endswith((".png", ".webp")):
            ext = ".png"

        file_path = self.cache_dir / f"{url_hash}{ext}"

        # Return if already cached
        if file_path.exists():
            return file_path

        # Download file
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url)
            response.raise_for_status()

            file_path.write_bytes(response.content)
            return file_path

    async def search_music(self, mood: str = "upbeat") -> Optional[Path]:
        """Search for background music (Pixabay Music API)."""
        if not self.pixabay_key:
            return None

        try:
            async with httpx.AsyncClient() as client:
                # Note: Pixabay doesn't have a dedicated music API in their free tier
                # This is a placeholder for future implementation or alternative sources
                pass
        except Exception as e:
            print(f"Error searching music: {e}")

        return None
