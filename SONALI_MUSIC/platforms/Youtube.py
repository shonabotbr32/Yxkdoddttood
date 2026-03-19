import asyncio
import re
import yt_dlp
from py_yt import VideosSearch

from SONALI_MUSIC import LOGGER

logger = LOGGER(__name__)


class YouTubeAPI:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"

    def is_url(self, text: str):
        return re.search(self.regex, text)

    # ✅ URL extract from message
    async def url(self, message):
        try:
            if message.text:
                parts = message.text.split()
                if len(parts) > 1:
                    return parts[1]
        except Exception as e:
            logger.error(f"url error: {e}")
        return None

    # ✅ URL check
    async def exists(self, url: str):
        return True if url else False

    # ✅ Search / Track
    async def track(self, query, videoid=False):
        try:
            if videoid:
                url = self.base + query
            elif self.is_url(query):
                url = query
            else:
                results = VideosSearch(query, limit=1)
                data = (await results.next())["result"][0]
                url = self.base + data["id"]

            def extract():
                ydl_opts = {
                    "quiet": True,
                    "format": "bestaudio/best",
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    return ydl.extract_info(url, download=False)

            info = await asyncio.to_thread(extract)

            details = {
                "title": info.get("title"),
                "duration_min": self.sec_to_min(info.get("duration")),
                "thumb": info.get("thumbnail"),
                "id": info.get("id"),
                "url": url,
            }

            return details, info.get("id")

        except Exception as e:
            logger.error(f"track error: {e}")
            return None, None

    # ✅ Playlist (basic)
    async def playlist(self, query, limit=10, user_id=None):
        try:
            results = VideosSearch(query, limit=limit)
            data = (await results.next())["result"]
            return [video["id"] for video in data]
        except Exception as e:
            logger.error(f"playlist error: {e}")
            return []

    # ✅ Stream URL (MOST IMPORTANT)
    async def video(self, link: str):
        def get_stream():
            try:
                ydl_opts = {
                    "quiet": True,
                    "format": "bestaudio/best",
                    "noplaylist": True,
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(link, download=False)
                    return info.get("url")
            except Exception as e:
                logger.error(f"stream error: {e}")
                return None

        url = await asyncio.to_thread(get_stream)

        if url:
            return 1, url
        return 0, None

    # ✅ helper
    def sec_to_min(self, seconds):
        if not seconds:
            return "Live"
        m, s = divmod(seconds, 60)
        return f"{int(m)}:{int(s):02d}"


YouTube = YouTubeAPI()
