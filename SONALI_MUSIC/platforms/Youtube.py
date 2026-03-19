import asyncio
import os
import re
from typing import Union

import yt_dlp
from py_yt import VideosSearch

from SONALI_MUSIC import LOGGER
from SONALI_MUSIC.utils.formatters import time_to_seconds

logger = LOGGER(__name__)


class YouTubeAPI:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"

    def is_url(self, text: str):
        return re.search(self.regex, text)

    async def details(self, query: str):
        try:
            # 🔥 URL handle
            if self.is_url(query):
                return await self.get_from_url(query)

            # 🔍 search handle
            results = VideosSearch(query, limit=1)
            data = (await results.next())["result"][0]

            return (
                data["title"],
                data["duration"],
                int(time_to_seconds(data["duration"])) if data["duration"] else 0,
                data["thumbnails"][0]["url"].split("?")[0],
                data["id"],
            )
        except Exception as e:
            logger.error(f"Details error: {e}")
            return None

    async def get_from_url(self, url: str):
        def extract():
            try:
                with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
                    return ydl.extract_info(url, download=False)
            except Exception as e:
                logger.error(f"URL extract error: {e}")
                return None

        info = await asyncio.to_thread(extract)

        if not info:
            return None

        return (
            info.get("title"),
            info.get("duration"),
            info.get("duration"),
            info.get("thumbnail"),
            info.get("id"),
        )

    async def video(self, link: str):
        def get_stream():
            try:
                with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
                    info = ydl.extract_info(link, download=False)
                    return info.get("url")
            except Exception as e:
                logger.error(f"Stream error: {e}")
                return None

        url = await asyncio.to_thread(get_stream)

        if url:
            return 1, url
        return 0, "Failed"

    async def download(
        self,
        link: str,
        mystic=None,
        video: Union[bool, str] = False,
    ):
        if not self.is_url(link):
            link = self.base + link

        ext = "mp4" if video else "mp3"

        def _download():
            try:
                ydl_opts = {
                    "format": "bestvideo[height<=720]+bestaudio/best"
                    if video
                    else "bestaudio/best",
                    "outtmpl": "downloads/%(id)s.%(ext)s",
                    "quiet": True,
                    "noplaylist": True,
                }

                if not video:
                    ydl_opts["postprocessors"] = [
                        {
                            "key": "FFmpegExtractAudio",
                            "preferredcodec": "mp3",
                            "preferredquality": "192",
                        }
                    ]

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(link, download=True)
                    return f"downloads/{info['id']}.{ext}"

            except Exception as e:
                logger.error(f"Download failed: {e}")
                return None

        return await asyncio.to_thread(_download)

    async def playlist(self, link, limit=10):
        try:
            results = VideosSearch(link, limit=limit)
            data = (await results.next())["result"]

            return [video["id"] for video in data]

        except Exception as e:
            logger.error(f"Playlist error: {e}")
            return []
