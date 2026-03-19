import asyncio
import re
import yt_dlp
from py_yt import VideosSearch


class YouTubeAPI:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"

    def is_url(self, text: str):
        return re.search(self.regex, text)

    # 🔥 GET URL FROM MESSAGE
    async def url(self, message):
        if message.text:
            parts = message.text.split()
            if len(parts) > 1:
                return parts[1]
        return None

    # 🔥 CHECK VALID URL
    async def exists(self, url: str):
        return True if url else False

    # 🔍 SEARCH / TRACK
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
                with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
                    return ydl.extract_info(url, download=False)

            info = await asyncio.to_thread(extract)

            details = {
                "title": info.get("title"),
                "duration_min": self.sec_to_min(info.get("duration")),
                "thumb": info.get("thumbnail"),
                "id": info.get("id"),
            }

            return details, info.get("id")

        except:
            return None, None

    # 🔥 PLAYLIST (basic)
    async def playlist(self, query, limit=10, user_id=None):
        results = VideosSearch(query, limit=limit)
        data = (await results.next())["result"]
        return [video["id"] for video in data]

    # 🔥 STREAM LINK
    async def video(self, link: str):
        def get_stream():
            with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
                info = ydl.extract_info(link, download=False)
                return info.get("url")

        url = await asyncio.to_thread(get_stream)
        return (1, url) if url else (0, None)

    # 🔧 HELPER
    def sec_to_min(self, seconds):
        if not seconds:
            return "Live"
        m, s = divmod(seconds, 60)
        return f"{int(m)}:{int(s):02d}"


YouTube = YouTubeAPI()
