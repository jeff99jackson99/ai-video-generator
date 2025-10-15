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
        media_type: str = "photos"  # "photos" or "videos"
    ) -> List[Path]:
        """Search for and download media based on keywords."""
        all_media = []
        
        # Try each API source
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
        for media_url in all_media[:count]:
            try:
                file_path = await self._download_file(media_url)
                if file_path:
                    downloaded.append(file_path)
            except Exception as e:
                print(f"Error downloading {media_url}: {e}")
        
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
        """Generate placeholder media when no API keys available."""
        placeholders = []
        
        for i, keyword in enumerate(keywords[:count]):
            if media_type == "photos":
                # Create colored placeholder image
                file_path = self.cache_dir / f"placeholder_{i}_{keyword[:20]}.jpg"
                if not file_path.exists():
                    # Create a simple colored image
                    color = (
                        (i * 50) % 255,
                        (i * 100) % 255,
                        (i * 150) % 255
                    )
                    img = Image.new('RGB', (1920, 1080), color=color)
                    img.save(file_path, 'JPEG')
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

