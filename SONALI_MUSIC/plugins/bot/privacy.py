from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from SONALI_MUSIC import app

@app.on_message(filters.command("privacy"))
async def privacy_command(client: Client, message: Message):
    await message.reply_photo(
        photo="https://files.catbox.moe/0jpf7u.jpg",
        caption="**➻ ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ 𝗦𝗵𝗼𝗻𝗮 𝗡𝗲𝘁𝘄𝗼𝗿𝗸 ʙᴏᴛꜱ ᴘʀɪᴠᴀᴄʏ ᴘᴏʟɪᴄʏ.**\n\n**⊚ ᴄʟɪᴄᴋ ᴛʜᴇ ʙᴇʟᴏᴡ ʙᴜᴛᴛᴏɴ ᴛʜᴇɴ ꜱᴇᴇ ᴘʀɪᴠᴀᴄʏ ᴘᴏʟɪᴄʏ 🔏**",
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("˹ ᴘʀɪᴠᴀᴄʏ ˼", url="https://telegra.ph/ANONYMOUS---SHONA-BOTS-03-14")]
            ]
        )
    )

# ======================================================
# ©️ 2025-26 All Rights Reserved by Purvi Bots (Im-Notcoder) 😎

# 🧑‍💻 Developer : t.me/TheSigmaCoder
# 🔗 Source link : GitHub.com/Im-Notcoder/Sonali-MusicV2
# 📢 Telegram channel : t.me/Purvi_Bots
# =======================================================
