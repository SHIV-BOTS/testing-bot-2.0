import asyncio
import random
from pyrogram import filters
from pyrogram.enums import ButtonStyle
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from PritiMusic import app
from config import LOGGER_ID, SUDOERS
from PritiMusic.utils.database.leaderboard import get_leaderboard, reset_leaderboard

# 💎 Premium Emojis ID List
PREMIUM_EMOJIS = [
    5258362837411045098, 6102938383456146362, 5463274047771000031, 6100397162976252509,
    5373310679241466020, 5408916593780470262, 5776182936638329359, 5258389041006518073,
    6280269890821558384, 5936143551854285132, 6172332822892647766, 5891211339170326418,
    5409368076447657845, 6172312314423808834, 6082387600599944892, 6271537028307881531
]

# 👑 Specific Emojis For Leaderboard Buttons
EMOJI_LEADERBOARD = 5936143551854285132  # 📊 (Chart/Stats)
EMOJI_CROWN = 6237864166879663987        # 👑 (Crown)

# 🎨 Dynamic Color Generator
def get_style_map():
    styles = [ButtonStyle.PRIMARY, ButtonStyle.SUCCESS, ButtonStyle.DANGER]
    random.shuffle(styles)
    return {1: styles[0], 2: styles[1], 3: styles[2], 4: styles[0]}

# 🔘 Smart Button Creator
def create_btn(text, cb=None, url=None, user_id=None, style=ButtonStyle.PRIMARY, emoji_id=None, no_emoji=False):
    kwargs = {"text": text, "style": style}
    if cb: kwargs["callback_data"] = cb
    if url: kwargs["url"] = url
    if user_id: kwargs["user_id"] = user_id
    
    if emoji_id:
        kwargs["icon_custom_emoji_id"] = int(emoji_id)
    elif not no_emoji:
        kwargs["icon_custom_emoji_id"] = int(random.choice(PREMIUM_EMOJIS))
        
    return InlineKeyboardButton(**kwargs)

# Apna Main Bot ka username yahan daalein (Bina @ ke)
MAIN_BOT_USERNAME = "clone_MUSICrobot"

# ----------------- LEADERBOARD COMMANDS ----------------- #

@app.on_message(filters.command("leaderboard"))
async def show_leaderboard(client, message):
    bot_username = client.me.username
    
    # 1. CLONE BOT LOGIC: Redirect to Main Bot
    if bot_username.lower() != MAIN_BOT_USERNAME.lower():
        style_map = get_style_map()
        button = InlineKeyboardMarkup([
            [create_btn(text="View Leaderboard", url=f"https://t.me/{MAIN_BOT_USERNAME}?start=leaderboard", style=style_map[1], emoji_id=EMOJI_LEADERBOARD)]
        ])
        
        return await message.reply_text(
            "<tg-emoji emoji-id=\"6102938383456146362\">⚠️</tg-emoji> **The Leaderboard is only available in the Main Bot!**\n\nClick the button below to check the monthly clone rankings and win gifts! <tg-emoji emoji-id=\"6172312314423808834\">✨</tg-emoji>",
            reply_markup=button
        )
        
    # 2. MAIN BOT LOGIC: Show actual leaderboard
    top_bots = await get_leaderboard()
    
    if not top_bots:
        return await message.reply_text("<tg-emoji emoji-id=\"6271611232457855630\">❌</tg-emoji> **No clone bots have played any songs yet this month!**")
        
    text = "<tg-emoji emoji-id=\"6237864166879663987\">👑</tg-emoji> **MONTHLY CLONE LEADERBOARD** <tg-emoji emoji-id=\"6237864166879663987\">👑</tg-emoji>\n\n"
    text += "This is a monthly leaderboard! The owner of the top-ranked bot—meaning the clone bot with the highest number of users and song plays—will receive a gift! 😂\n\n"
    text += "<tg-emoji emoji-id=\"5408843502027033965\">📦</tg-emoji> **THE GIFTS ARE —**\n"
    text += "<tg-emoji emoji-id=\"6125264332130359953\">🌟</tg-emoji> **1st Place:** 1 month YouTube Premium, 1 month Gemini, or 1 TG account <tg-emoji emoji-id=\"6172312314423808834\">✨</tg-emoji>\n"
    text += "🥈 **2nd Place:** 1 month YouTube Premium 😀\n\n"
    text += "<tg-emoji emoji-id=\"5355051922862653659\">🤖</tg-emoji> **Top Bots This Month:**\n"
    
    for rank, bot in enumerate(top_bots, start=1):
        text += f"**{rank}.** @{bot['bot_username']} - `{bot['plays']}` Plays\n"
        
    await message.reply_text(text)

@app.on_message(filters.command("resetleaderboard") & filters.user(SUDO_USERS))
async def clean_monthly_lb(client, message):
    """Owner command to wipe leaderboard at the end of the month."""
    await reset_leaderboard()
    await message.reply_text("<tg-emoji emoji-id=\"6280269890821558384\">✅</tg-emoji> **Monthly leaderboard has been successfully cleaned!**")

# ----------------- HOURLY LOGGER LOGIC ----------------- #

async def send_hourly_leaderboard():
    """Yeh function har 1 ghante mein automatically run hoga."""
    if not LOGGER_ID:
        return
        
    # Database se top 10 bots fetch karo
    top_bots = await get_leaderboard()
    
    if not top_bots:
        return # Agar kisi ne play nahi kiya toh message mat bhejo
        
    text = "<tg-emoji emoji-id=\"5936143551854285132\">📊</tg-emoji> **HOURLY CLONE LEADERBOARD UPDATE** <tg-emoji emoji-id=\"5936143551854285132\">📊</tg-emoji>\n\n"
    text += "<tg-emoji emoji-id=\"5355051922862653659\">🤖</tg-emoji> **Top 10 Clone Bots based on Song Plays:**\n\n"
    
    for rank, bot in enumerate(top_bots, start=1):
        text += f"**{rank}.** @{bot['bot_username']} - `{bot['plays']}` Plays\n"
        
    text += "\n<tg-emoji emoji-id=\"6172312314423808834\">✨</tg-emoji> **Keep playing to win monthly gifts!**"
    
    # Button jo main bot par redirect karega
    style_map = get_style_map()
    button = InlineKeyboardMarkup([
        [create_btn(text="View Full Leaderboard", url=f"https://t.me/{app.me.username}?start=leaderboard", style=style_map[1], emoji_id=EMOJI_LEADERBOARD)]
    ])
    
    try:
        # Logger group mein message bhejna
        await app.send_message(
            chat_id=LOGGER_ID,
            text=text,
            reply_markup=button
        )
    except Exception as e:
        print(f"Hourly Leaderboard Logger Error: {e}")

# Scheduler Initialize aur Start karna
scheduler = AsyncIOScheduler()
# Interval ko 1 hour set kiya gaya hai
scheduler.add_job(send_hourly_leaderboard, "interval", hours=1)
scheduler.start()
