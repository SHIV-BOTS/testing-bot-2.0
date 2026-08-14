from pyrogram import filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup
from PritiMusic import app

# Yahan par apni UI file import karein (jahan eq_markup hai)
from PritiMusic.utils.inline.play import eq_markup

# Agar aapke bot mein Call class alag hai (jahan change_volume/filter methods hain),
# toh use yahan import kar lijiye, e.g.:
# from PritiMusic.core.call import PritiMusic


# ----------------------------------------------------
# 🎛 EQUALIZER MENU OPENER
# ----------------------------------------------------
@app.on_callback_query(filters.regex(r"^EQMenu"))
async def eq_menu_callback(client, query: CallbackQuery):
    try:
        # Chat ID nikalna query se (Format: EQMenu|chat_id)
        chat_id = int(query.data.split("|")[1])
    except:
        chat_id = query.message.chat.id
        
    # Naya EQ markup fetch karo
    keyboard = InlineKeyboardMarkup(eq_markup(None, chat_id))
    
    # Message ka inline keyboard update kar do
    await query.edit_message_reply_markup(reply_markup=keyboard)
    await query.answer("Equalizer & Volume Menu Opened 🎛", show_alert=False)


# ----------------------------------------------------
# 🔉 VOLUME CONTROLLER & BOOSTER LOGIC
# ----------------------------------------------------
# Memory dictionary to store volume without database
active_volumes = {}

@app.on_callback_query(filters.regex(r"^vol_"))
async def vol_controls(client, query: CallbackQuery):
    try:
        # Format: vol_up|chat_id
        action, chat_id = query.data.split("|")
        chat_id = int(chat_id)
    except:
        action = query.data
        chat_id = query.message.chat.id

    # Default volume is 100
    current_vol = active_volumes.get(chat_id, 100)

    if action == "vol_up":
        # Hardcore 10000 limit with +50 steps
        current_vol = min(current_vol + 50, 10000) 
    elif action == "vol_down":
        # Min limit 0 with -50 steps
        current_vol = max(current_vol - 50, 0)
    elif action == "vol_boost":
        # Insta Booster (500% directly)
        current_vol = 500 

    # Save to memory
    active_volumes[chat_id] = current_vol
    
    # --- PYTGCALLS VOLUME UPDATE ---
    # Aapki main stream file ke hisaab se is line ko uncomment aur adjust karein
    # try:
    #     await PritiMusic.change_volume(chat_id, current_vol)
    # except Exception as e:
    #     print(f"Volume Update Error: {e}")
    
    await query.answer(f"🔊 Volume Updated: {current_vol}%", show_alert=True)


# ----------------------------------------------------
# 🎧 EQUALIZER PRESETS & DJ REMIX LOGIC
# ----------------------------------------------------
@app.on_callback_query(filters.regex(r"^eq_"))
async def eq_controls(client, query: CallbackQuery):
    try:
        # Format: eq_bass|chat_id
        action, chat_id = query.data.split("|")
        chat_id = int(chat_id)
    except:
        action = query.data
        chat_id = query.message.chat.id
        
    # Remove "eq_" prefix to get exact filter name
    action_name = action.replace("eq_", "")
    
    # FFmpeg Filters Dictionary
    filters_map = {
        "8d": "apulsator=hz=0.125",
        "auditorium": "aecho=0.8:0.9:1000:0.3",
        "bass": "bass=g=15",
        "club": "bass=g=10,treble=g=5",
        "dj": "bass=g=20,treble=g=10,compand=attacks=0:points=-80/-80|-15/-15|0/-5.0|20/-5.0", # Heavy Club/DJ Effect
        "slowed": "atempo=0.85,aecho=0.8:0.9:1000:0.3",
        "nightcore": "asetrate=48000*1.25,aresample=48000",
        "normal": "anull" # Flat / Reset
    }
    
    selected_filter = filters_map.get(action_name, "anull")
    
    # --- PYTGCALLS FILTER UPDATE ---
    # Aapki main stream file ke hisaab se is line ko uncomment aur adjust karein
    # (Yeh stream engine ke audio parameters update karne ke liye hai)
    # try:
    #     await PritiMusic.change_stream_filter(chat_id, selected_filter)
    # except Exception as e:
    #     print(f"Filter Update Error: {e}")
    
    emoji = "🎧" if action_name in ["dj", "bass", "club"] else "🎛"
    await query.answer(f"{emoji} Mode Set: {action_name.title()}", show_alert=True)
