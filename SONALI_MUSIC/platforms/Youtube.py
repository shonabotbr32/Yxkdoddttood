import asyncio
import os
import re
import random
import aiohttp
import yt_dlp
from typing import Union
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from py_yt import VideosSearch
from SONALI_MUSIC.utils.database import is_on_off
from SONALI_MUSIC.utils.formatters import time_to_seconds
from config import YT_API_KEY, YTPROXY_URL as YTPROXY

# SAFE FOLDERS
os.makedirs("downloads", exist_ok=True)
os.makedirs("cookies", exist_ok=True)


def extract_video_id(link: str):
    pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11})"
    match = re.search(pattern, link)
    return match.group(1) if match else None


def cookie_txt_file():
    cookie_dir = os.path.join(os.getcwd(), "cookies")
    files = [f for f in os.listdir(cookie_dir) if f.endswith(".txt")]
    if not files:
        return None
    return os.path.join(cookie_dir, random.choice(files))


async def download_song(link: str):
    video_id = extract_video_id(link)
    if not video_id:
        return None

    download_folder = "downloads"

    for ext in ["mp3", "m4a", "webm"]:
        path = f"{download_folder}/{video_id}.{ext}"
        if os.path.exists(path):
            return path

    song_url = f"{YTPROXY}/song/{video_id}?api={YT_API_KEY}"

    async with aiohttp.ClientSession() as session:
        for _ in range(10):

            async with session.get(song_url) as response:
                if response.status != 200:
                    await asyncio.sleep(3)
                    continue

                data = await response.json()
                status = data.get("status", "").lower()

                if status == "done":
                    download_url = data.get("link")
                    break

                if status == "downloading":
                    await asyncio.sleep(4)
                else:
                    return None

        else:
            return None

        ext = data.get("format", "mp3")
        path = f"{download_folder}/{video_id}.{ext}"

        async with session.get(download_url) as file:
            with open(path, "wb") as f:
                while True:
                    chunk = await file.content.read(8192)
                    if not chunk:
                        break
                    f.write(chunk)

        return path


async def download_video(link: str):
    video_id = extract_video_id(link)
    if not video_id:
        return None

    download_folder = "downloads"

    for ext in ["mp4", "webm", "mkv"]:
        path = f"{download_folder}/{video_id}.{ext}"
        if os.path.exists(path):
            return path

    video_url = f"{YTPROXY}/video/{video_id}?api={YT_API_KEY}"

    async with aiohttp.ClientSession() as session:
        for _ in range(10):

            async with session.get(video_url) as response:
                if response.status != 200:
                    await asyncio.sleep(4)
                    continue

                data = await response.json()
                status = data.get("status", "").lower()

                if status == "done":
                    download_url = data.get("link")
                    break

                if status == "downloading":
                    await asyncio.sleep(6)
                else:
                    return None

        else:
            return None

        ext = data.get("format", "mp4")
        path = f"{download_folder}/{video_id}.{ext}"

        async with session.get(download_url) as file:
            with open(path, "wb") as f:
                while True:
                    chunk = await file.content.read(8192)
                    if not chunk:
                        break
                    f.write(chunk)

        return path


class YouTubeAPI:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"

    async def exists(self, link: str):
        return bool(re.search(self.regex, link))

    async def url(self, message: Message) -> Union[str, None]:
        messages = [message]

        if message.reply_to_message:
            messages.append(message.reply_to_message)

        for msg in messages:

            if msg.entities:

                for entity in msg.entities:

                    if entity.type == MessageEntityType.URL:

                        text = msg.text or msg.caption
                        return text[entity.offset : entity.offset + entity.length]

        return None

    async def track(self, link: str):

        results = VideosSearch(link, limit=1)

        data = (await results.next())["result"][0]

        title = data["title"]
        duration = data["duration"]
        vidid = data["id"]
        thumb = data["thumbnails"][0]["url"].split("?")[0]
        yturl = data["link"]

        return {
            "title": title,
            "link": yturl,
            "vidid": vidid,
            "duration_min": duration,
            "thumb": thumb,
        }, vidid

    async def video(self, link: str):

        try:
            file = await download_video(link)
            if file:
                return 1, file
        except:
            pass

        cookie = cookie_txt_file()

        if not cookie:
            return 0, "No cookies found."

        proc = await asyncio.create_subprocess_exec(
            "yt-dlp",
            "--cookies",
            cookie,
            "-g",
            "-f",
            "best[height<=?720]",
            link,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, stderr = await proc.communicate()

        if stdout:
            return 1, stdout.decode().split("\n")[0]

        return 0, stderr.decode()

    async def download(self, link: str, songaudio=False, songvideo=False, video=False):

        if songaudio or songvideo:
            return await download_song(link)

        if video:
            return await download_video(link)

        return None
