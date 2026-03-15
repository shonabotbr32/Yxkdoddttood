import asyncio
import os
import re
import random
import aiohttp
import yt_dlp
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from py_yt import VideosSearch
from typing import Union
from config import YT_API_KEY, YTPROXY_URL as YTPROXY

# AUTO CREATE FOLDERS
os.makedirs("downloads", exist_ok=True)
os.makedirs("cookies", exist_ok=True)


def extract_video_id(url: str):
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", url)
    return match.group(1) if match else None


def cookie_txt_file():
    cookie_dir = f"{os.getcwd()}/cookies"

    cookies = [f for f in os.listdir(cookie_dir) if f.endswith(".txt")]

    if not cookies:
        return None

    return os.path.join(cookie_dir, random.choice(cookies))


async def download_song(link: str):

    video_id = extract_video_id(link)

    if not video_id:
        return None

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

                elif status == "downloading":
                    await asyncio.sleep(4)

                else:
                    return None

        else:
            return None

        ext = data.get("format", "mp3")
        file_path = f"downloads/{video_id}.{ext}"

        async with session.get(download_url) as file_response:

            with open(file_path, "wb") as f:

                while True:

                    chunk = await file_response.content.read(8192)

                    if not chunk:
                        break

                    f.write(chunk)

        return file_path


async def download_video(link: str):

    video_id = extract_video_id(link)

    if not video_id:
        return None

    video_url = f"{YTPROXY}/video/{video_id}?api={YT_API_KEY}"

    async with aiohttp.ClientSession() as session:

        for _ in range(10):

            async with session.get(video_url) as response:

                if response.status != 200:
                    await asyncio.sleep(3)
                    continue

                data = await response.json()
                status = data.get("status", "").lower()

                if status == "done":
                    download_url = data.get("link")
                    break

                elif status == "downloading":
                    await asyncio.sleep(5)

                else:
                    return None

        else:
            return None

        ext = data.get("format", "mp4")
        file_path = f"downloads/{video_id}.{ext}"

        async with session.get(download_url) as file_response:

            with open(file_path, "wb") as f:

                while True:

                    chunk = await file_response.content.read(8192)

                    if not chunk:
                        break

                    f.write(chunk)

        return file_path


class YouTubeAPI:

    def __init__(self):
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

                        return text[
                            entity.offset : entity.offset + entity.length
                        ]

        return None

    async def track(self, link: str):

        try:

            results = VideosSearch(link, limit=1)

            search = await results.next()

            if not search["result"]:
                return None, None

            data = search["result"][0]

            title = data.get("title")
            vidid = data.get("id")
            duration = data.get("duration")
            thumb = data["thumbnails"][0]["url"].split("?")[0]
            yturl = data.get("link")

            track_details = {
                "title": title,
                "link": yturl,
                "vidid": vidid,
                "duration_min": duration,
                "thumb": thumb,
            }

            return track_details, vidid

        except Exception as e:
            print(f"Track Error: {e}")
            return None, None

    async def video(self, link: str):

        try:

            file = await download_video(link)

            if file:
                return 1, file

        except:
            pass

        cookie = cookie_txt_file()

        if not cookie:
            return 0, "No cookies found"

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

            file = await download_song(link)

            return file

        if video:

            file = await download_video(link)

            return file

        return None9
