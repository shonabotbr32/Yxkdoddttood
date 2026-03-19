import asyncio

from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import (
    ChatAdminRequired,
    InviteRequestSent,
    UserAlreadyParticipant,
    UserNotParticipant,
)
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from SONALI_MUSIC import YouTube, app
from SONALI_MUSIC.misc import SUDOERS
from SONALI_MUSIC.utils.database import (
    get_assistant,
    get_cmode,
    get_lang,
    get_playmode,
    get_playtype,
    is_active_chat,
    is_maintenance,
)
from SONALI_MUSIC.utils.inline import botplaylist_markup
from config import PLAYLIST_IMG_URL, SUPPORT_CHAT, adminlist
from strings import get_string

links = {}


def PlayWrapper(command):
    async def wrapper(client, message):
        language = await get_lang(message.chat.id)
        _ = get_string(language)

        if message.sender_chat:
            upl = InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="HOW TO FIX ?", callback_data="SonamousAdmin")]]
            )
            return await message.reply_text(_["general_3"], reply_markup=upl)

        if await is_maintenance() is False:
            if message.from_user.id not in SUDOERS:
                return await message.reply_text(
                    text=f"{app.mention} is under maintenance, visit support chat.",
                    disable_web_page_preview=True,
                )

        try:
            await message.delete()
        except:
            pass

        # 🔥 FIXED QUERY SYSTEM (NO url())
        query = None
        if message.text and len(message.text.split()) > 1:
            query = message.text.split(None, 1)[1]

        audio_telegram = (
            (message.reply_to_message.audio or message.reply_to_message.voice)
            if message.reply_to_message
            else None
        )
        video_telegram = (
            (message.reply_to_message.video or message.reply_to_message.document)
            if message.reply_to_message
            else None
        )

        if audio_telegram is None and video_telegram is None and query is None:
            if len(message.command) < 2:
                if "stream" in message.command:
                    return await message.reply_text(_["str_1"])
                buttons = botplaylist_markup(_)
                return await message.reply_photo(
                    photo=PLAYLIST_IMG_URL,
                    caption=_["play_18"],
                    reply_markup=InlineKeyboardMarkup(buttons),
                )

        # CHAT MODE
        if message.command[0][0] == "c":
            chat_id = await get_cmode(message.chat.id)
            if chat_id is None:
                return await message.reply_text(_["setting_7"])
            try:
                chat = await app.get_chat(chat_id)
                channel = chat.title
            except:
                return await message.reply_text(_["cplay_4"])
        else:
            chat_id = message.chat.id
            channel = None

        playmode = await get_playmode(message.chat.id)
        playty = await get_playtype(message.chat.id)

        # PERMISSION CHECK
        if playty != "Everyone":
            if message.from_user.id not in SUDOERS:
                admins = adminlist.get(message.chat.id)
                if not admins:
                    return await message.reply_text(_["admin_13"])
                if message.from_user.id not in admins:
                    return await message.reply_text(_["play_4"])

        # VIDEO CHECK
        if message.command[0][0] == "v":
            video = True
        else:
            video = True if "-v" in message.text else None

        # FORCE PLAY
        if message.command[0][-1] == "e":
            if not await is_active_chat(chat_id):
                return await message.reply_text(_["play_16"])
            fplay = True
        else:
            fplay = None

        # JOIN ASSISTANT
        if not await is_active_chat(chat_id):
            userbot = await get_assistant(chat_id)
            try:
                member = await app.get_chat_member(chat_id, userbot.id)
                if member.status in [ChatMemberStatus.BANNED, ChatMemberStatus.RESTRICTED]:
                    return await message.reply_text(_["call_2"])
            except UserNotParticipant:
                try:
                    invitelink = await app.export_chat_invite_link(chat_id)
                    await userbot.join_chat(invitelink)
                except Exception as e:
                    return await message.reply_text(f"Join error: {e}")

        # 🔥 FINAL CALL (query pass ho raha hai)
        return await command(
            client,
            message,
            _,
            chat_id,
            video,
            channel,
            playmode,
            query,   # 🔥 FIXED
            fplay,
        )

    return wrapper
