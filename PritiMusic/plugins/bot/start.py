import time
import random
import asyncio
from pyrogram import filters
from pyrogram.enums import ChatType, ChatAction
from pyrogram.types import InlineKeyboardMarkup, Message, InlineKeyboardButton
from youtubesearchpython.__future__ import VideosSearch

# Import InputRichMessage from ftmgram
from ftmgram.types import InputRichMessage

import config
from PritiMusic import app
from PritiMusic.misc import _boot_
from PritiMusic.plugins.sudo.sudoers import sudoers_list
from PritiMusic.plugins.tools.leaderboard import show_leaderboard 
from PritiMusic.utils.database import (
    add_served_chat,
    add_served_user,
    blacklisted_chats,
    get_lang,
    is_banned_user,
    is_on_off,
)
from PritiMusic.utils.decorators.language import LanguageStart
from PritiMusic.utils.formatters import get_readable_time
from PritiMusic.utils.inline import help_pannel, start_panel
from config import BANNED_USERS, START_IMG_URL, CMBOT
from strings import get_string

PREMIUM_EMOJIS = [
    "5258362837411045098", "6102938383456146362", "5463274047771000031", "6100397162976252509",
    "5373310679241466020", "5408916593780470262", "5776182936638329359", "5258389041006518073",
    "6280269890821558384", "5936143551854285132", "6172332822892647766", "5891211339170326418",
    "5409368076447657845", "6172312314423808834", "6082387600599944892", "6271537028307881531"
]

def create_btn(text, cb=None, url=None, user_id=None):
    kwargs = {"text": text}
    if cb: kwargs["callback_data"] = cb
    if url: kwargs["url"] = url
    if user_id: kwargs["user_id"] = user_id
    return InlineKeyboardButton(**kwargs)

# 👇 HTML Builder integrated with ftmgram formatting
def build_welcome_html(user_mention: str, bot_mention: str, bot_username: str) -> str:
    support_link = config.SUPPORT_CHAT if hasattr(config, 'SUPPORT_CHAT') else "https://t.me/theshiv_support"
    update_link = config.SUPPORT_CHANNEL if hasattr(config, 'SUPPORT_CHANNEL') else "https://t.me/theshiv_updates"
    
    return f"""
💐 <b>Greetings, {user_mention}!</b> 🥀<br/><br/>

💮 <b>ᴛʜɪs ɪs {bot_mention} <tg-emoji emoji-id='6172312314423808834'>✨</tg-emoji> : The Ultimate Destination For High-Quality Streaming.</b><br/><br/>

<b><tg-emoji emoji-id='5408916593780470262'>🎧</tg-emoji> ϻυsɪᴄ ᴘʟᴧʏєʀ ᴡɪᴛʜ ᴄʟσηє ғєᴧᴛυʀєs</b><br/>
<b><tg-emoji emoji-id='5355051922862653659'>🤖</tg-emoji> ᴄʀєᴧᴛє ʏσυʀ σᴡη ʙσᴛ ɪηsᴛᴧηᴛʟʏ</b><br/><br/>

<blockquote expandable>
<b>Bot Information</b><br/><br/>

<b>Bot Reference</b><br/>
<table border="1">
  <tr>
    <th>Key</th>
    <th>Information</th>
  </tr>
  <tr>
    <td>Audio</td>
    <td>Dolby-Atmos</td>
  </tr>
  <tr>
    <td>Clone</td>
    <td>Advance</td>
  </tr>
  <tr>
    <td>ᴧᴄᴛɪᴠє</td>
    <td>24x7</td>
  </tr>
  <tr>
    <td>AutoPlay</td>
    <td>Supported</td>
  </tr>
</table>
</blockquote><br/>

<blockquote>🎋 Click Help To See {bot_mention} 🎵 All Available Commands.</blockquote><br/>

<tg-button-row align="center">
  <tg-button type="url" style="success" url="https://t.me/{bot_username}?startgroup=true">👻 ADD ME TO YOUR GROUP</tg-button>
</tg-button-row>
<tg-button-row align="justify">
  <tg-button type="url" style="primary" url="https://t.me/SUKOON_S">🪄 DAD</tg-button>
  <tg-button type="url" style="primary" url="https://t.me/clone_MUSICrobot">🤖 CLONE</tg-button>
</tg-button-row>
<tg-button-row align="justify">
  <tg-button type="url" style="secondary" url="{support_link}">👻 SUPPORT</tg-button>
  <tg-button type="url" style="secondary" url="{update_link}">⭐ SOURCE</tg-button>
</tg-button-row>
<tg-button-row align="center">
  <tg-button type="callback_data" style="primary" data="settings_back_helper">🎧 HELP AND COMMANDS</tg-button>
</tg-button-row>
"""

@app.on_message(filters.command(["start"]) & filters.private & ~BANNED_USERS)
@LanguageStart
async def start_pm(client, message: Message, _):
    loading_1 = await message.reply_text(random.choice(CMBOT))
    await add_served_user(message.from_user.id)
    
    await loading_1.edit_text("<b><tg-emoji emoji-id='5373310679241466020'>🌀</tg-emoji> ᴌᴏᴀᴅɪɴɢ....</b>")
    await asyncio.sleep(0.3)

    await loading_1.edit_text("<b><tg-emoji emoji-id='5891211339170326418'>⌛️</tg-emoji> ꜱᴛᴀʀᴛɪɴɢ..ʙᴀʙʏ.❤️❤️</b>")
    await asyncio.sleep(0.3)

    await loading_1.edit_text("<b><tg-emoji emoji-id='5355051922862653659'>🤖</tg-emoji> ɪ ᴀᴍ ᴀʟɪᴠᴇ ʙᴀʙʏ❤️😌🫣🫣</b>")
    await asyncio.sleep(0.5)

    await loading_1.edit_text("<b><tg-emoji emoji-id='6172312314423808834'>✨</tg-emoji> BETA ʙᴏᴛs🫣🫣.</b>")
    await asyncio.sleep(0.5)

    await loading_1.delete()
    
    if len(message.text.split()) > 1:
        name = message.text.split(None, 1)[1]
        
        if name == "leaderboard":
            return await show_leaderboard(client, message)
            
        if name[0:4] == "help":
            keyboard = help_pannel(_)
            await app.send_chat_action(message.chat.id, ChatAction.TYPING)
            await message.reply_sticker("CAACAgUAAxkBAAFJgZ1qBGwx9Z9vW5BhG3dw0l1A5j4CyQACXRYAAuc-wVWs4--9DGlDKzsE")
            return await message.reply_photo(
                random.choice(START_IMG_URL),
                caption=_["help_1"].format(config.SUPPORT_CHAT),
                reply_markup=keyboard,
            )
            
        if name[0:3] == "sud":
            await sudoers_list(client=client, message=message, _=_)
            if await is_on_off(2):
                return await app.send_message(
                    chat_id=config.LOGGER_ID,
                    text=f"<tg-emoji emoji-id='6172312314423808834'>✨</tg-emoji> {message.from_user.mention} ᴊᴜsᴛ sᴛᴀʀᴛᴇᴅ ᴛʜᴇ ʙᴏᴛ ᴛᴏ ᴄʜᴇᴄᴋ <b>sᴜᴅᴏʟɪsᴛ</b>.",
                )
            return
            
        if name[0:3] == "inf":
            m = await message.reply_text("<tg-emoji emoji-id='5429571366384842791'>🔎</tg-emoji>")
            query = (str(name)).replace("info_", "", 1)
            query = f"https://www.youtube.com/watch?v={query}"
            
            try:
                results = VideosSearch(query, limit=1)
                search_data = await results.next()
                
                if not search_data or not search_data.get("result"):
                    return await m.edit_text("<tg-emoji emoji-id='6271611232457855630'>❌</tg-emoji> Track details not found.")

                result = search_data["result"][0]
                title = result.get("title", "Unknown Title")
                duration = result.get("duration", "Unknown Duration")
                views = result.get("viewCount", {}).get("short", "0")
                
                thumbnails = result.get("thumbnails", [])
                thumbnail = thumbnails[0]["url"].split("?")[0] if thumbnails else random.choice(START_IMG_URL)
                
                channellink = result.get("channel", {}).get("link", "")
                channel = result.get("channel", {}).get("name", "Unknown Channel")
                link = result.get("link", query)
                published = result.get("publishedTime", "Unknown Date")

                searched_text = _["start_6"].format(
                    title, duration, views, published, channellink, channel, app.mention
                )
                
                key = InlineKeyboardMarkup(
                    [
                        [
                            create_btn(text=_["S_B_8"], url=link),
                            create_btn(text=_["S_B_9"], url=config.SUPPORT_CHAT),
                        ],
                    ]
                )
                await m.delete()
                await app.send_photo(
                    chat_id=message.chat.id,
                    photo=thumbnail,
                    caption=searched_text,
                    reply_markup=key,
                )
                if await is_on_off(2):
                    return await app.send_message(
                        chat_id=config.LOGGER_ID,
                        text=f"<tg-emoji emoji-id='6172312314423808834'>✨</tg-emoji> {message.from_user.mention} ᴊᴜsᴛ sᴛᴀʀᴛᴇᴅ ᴛʜᴇ ʙᴏᴛ ᴛᴏ ᴄʜᴇᴄᴋ <b>ᴛʀᴀᴄᴋ ɪɴғᴏʀᴍᴀᴛɪᴏɴ</b>.",
                    )
            except Exception as e:
                return await m.edit_text(f"<tg-emoji emoji-id='6271611232457855630'>❌</tg-emoji> An error occurred: `{e}`")

    else:
        await app.send_chat_action(message.chat.id, ChatAction.TYPING)
        await message.reply_sticker("CAACAgUAAxkBAAFJgZ1qBGwx9Z9vW5BhG3dw0l1A5j4CyQACXRYAAuc-wVWs4--9DGlDKzsE")
        
        welcome_html = build_welcome_html(
            user_mention=message.from_user.mention, 
            bot_mention=app.mention,
            bot_username=app.username
        )
        
        # 👇 Reply functionality removed to fix the TypeError
        await app.send_rich_message(
            chat_id=message.chat.id,
            rich_message=InputRichMessage(html=welcome_html)
        )
        
        if await is_on_off(2):
            return await app.send_message(
                chat_id=config.LOGGER_ID,
                text=f"<tg-emoji emoji-id='6172312314423808834'>✨</tg-emoji> {message.from_user.mention} ᴊᴜsᴛ sᴛᴀʀᴛᴇᴅ ᴛʜᴇ ʙᴏᴛ.",
            )

@app.on_message(filters.command(["start"]) & filters.group & ~BANNED_USERS)
@LanguageStart
async def start_gp(client, message: Message, _):
    out = start_panel(_)
    uptime = int(time.time() - _boot_)
    await message.reply_photo(
        random.choice(START_IMG_URL),
        caption=_["start_1"].format(app.mention, get_readable_time(uptime)),
        reply_markup=InlineKeyboardMarkup(out),
    )
    return await add_served_chat(message.chat.id)

@app.on_message(filters.new_chat_members, group=-1)
async def welcome(client, message: Message):
    for member in message.new_chat_members:
        try:
            language = await get_lang(message.chat.id)
            _ = get_string(language)
            if await is_banned_user(member.id):
                try:
                    await message.chat.ban_member(member.id)
                except:
                    pass
            if member.id == app.id:
                if message.chat.type != ChatType.SUPERGROUP:
                    await message.reply_text(_["start_4"])
                    return await app.leave_chat(message.chat.id)
                if message.chat.id in await blacklisted_chats():
                    await message.reply_text(
                        _["start_5"].format(app.mention, f"https://t.me/{app.username}?start=sudolist", config.SUPPORT_CHAT),
                        disable_web_page_preview=True,
                    )
                    return await app.leave_chat(message.chat.id)

                out = start_panel(_)
                await message.reply_text(
                    text=_["start_3"].format(message.from_user.mention, app.mention, message.chat.title, app.mention),
                    reply_markup=InlineKeyboardMarkup(out),
                )
                await add_served_chat(message.chat.id)
                await message.stop_propagation()
        except Exception as ex:
            print(ex)
