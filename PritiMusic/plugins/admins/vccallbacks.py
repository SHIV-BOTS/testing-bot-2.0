from pyrogram import filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup
from PritiMusic import app
from PritiMusic.core.call import Lucky
import config

# UI Import (Jahan se Equalizer buttons aate hain)
try:
    from PritiMusic.utils.inline.play import eq_markup
except ImportError:
    pass

# Memory dictionary volume store karne ke liye
active_volumes = {}

# ----------------------------------------------------
# 🎛 EQUALIZER MENU OPENER (Timer Fix ke sath)
# ----------------------------------------------------
@app.on_callback_query(filters.regex(r"^EQMenu"))
async def eq_menu_callback(client, query: CallbackQuery):
    try:
        chat_id = int(query.data.split("|")[1])
    except:
        chat_id = query.message.chat.id
        
    # 👉🏻 TIMER FIX: Jaise hi menu open ho, chat_id ko EQ_CHATS list me daal do 
    # Taki callback.py wala timer is menu ko auto-close na kare.
    if not hasattr(config, "EQ_CHATS"):
        config.EQ_CHATS = []
    if chat_id not in config.EQ_CHATS:
        config.EQ_CHATS.append(chat_id)
        
    try:
        keyboard = InlineKeyboardMarkup(eq_markup(None, chat_id))
        await query.edit_message_reply_markup(reply_markup=keyboard)
        await query.answer("Equalizer & Volume Menu Opened 🎛", show_alert=False)
    except Exception as e:
        print(f"EQ Menu Error: {e}")


# ----------------------------------------------------
# 🔉 VOLUME CONTROLLER & BOOSTER LOGIC
# ----------------------------------------------------
@app.on_callback_query(filters.regex(r"^vol_"))
async def vol_controls(client, query: CallbackQuery):
    try:
        action, chat_id = query.data.split("|")
        chat_id = int(chat_id)
    except:
        action = query.data
        chat_id = query.message.chat.id

    # Default Telegram volume 100% hoti hai
    current_vol = active_volumes.get(chat_id, 100)

    if action == "vol_up":
        # Har click par +50 badhega (Max 10,000)
        current_vol = min(current_vol + 50, 10000) 
    elif action == "vol_down":
        # Har click par -20 kam hoga (Min 0)
        current_vol = max(current_vol - 20, 0)
    elif action == "vol_boost":
        # Booster par direct +500 ka jump lagega
        current_vol = min(current_vol + 500, 10000) 

    active_volumes[chat_id] = current_vol
    
    # Music Engine ko volume set karne ka command
    try:
        await Lucky.change_volume_call(chat_id, current_vol)
    except AttributeError:
        try:
            await Lucky.change_volume(chat_id, current_vol)
        except Exception:
            pass
    except Exception:
        pass
    
    # User ko alert dikhane ke liye
    if current_vol >= 10000:
        msg = "🚀 ᴍᴀx ʙᴏᴏsᴛ ᴀᴄᴛɪᴠᴀᴛᴇᴅ : 10,000% (🔥 FULL HIGH!)"
    elif current_vol <= 0:
        msg = "🔇 ᴍᴜsɪᴄ ᴍᴜᴛᴇᴅ : 0%"
    else:
        msg = f"🔊 ᴠᴏʟᴜᴍᴇ : {current_vol}%"

    await query.answer(msg, show_alert=True)


# ----------------------------------------------------
# 🎧 EQUALIZER PRESETS & DJ REMIX LOGIC
# ----------------------------------------------------
@app.on_callback_query(filters.regex(r"^eq_"))
async def eq_controls(client, query: CallbackQuery):
    try:
        action, chat_id = query.data.split("|")
        chat_id = int(chat_id)
    except:
        action = query.data
        chat_id = query.message.chat.id
        
    action_name = action.replace("eq_", "")
    
    # Asli Hardcore FFMPEG Filters 🪄
    filters_map = {
        "8d": "apulsator=hz=0.125",
        "auditorium": "aecho=0.8:0.9:1000:0.3",
        "bass": "bass=g=25:f=110:w=0.3",
        "club": "bass=g=15,treble=g=5",
        "dj": "asetrate=44100*1.15,atempo=1.15,bass=g=15:f=110:w=0.6,treble=g=5",
        "slowed": "asetrate=44100*0.85,atempo=0.85,aecho=0.8:0.9:1000:0.3",
        "nightcore": "asetrate=48000*1.25,aresample=48000",
        "normal": "anull"
    }
    
    selected_filter = filters_map.get(action_name, "anull")
    
    # Music engine ko filter set karne ka command
    try:
        await Lucky.change_filter(chat_id, selected_filter)
    except AttributeError:
        try:
            await Lucky.change_stream_filter(chat_id, selected_filter)
        except Exception:
            pass
    except Exception:
        pass
    
    emoji = "🎧" if action_name in ["dj", "bass", "club"] else "🎛"
    await query.answer(f"{emoji} Mode Set: {action_name.title()}", show_alert=True)


# ----------------------------------------------------
# 🔙 BACK BUTTON HANDLER (EQ Menu close karne par timer wapas chalu karne ke liye)
# ----------------------------------------------------
@app.on_callback_query(filters.regex(r"^PanelMarkup None"))
async def eq_back_handler(client, query: CallbackQuery):
    # Yeh code sure karega ki jab user EQ Menu se 'Back' dabaye, 
    # tab timer wapas chalna shuru ho jaye.
    try:
        chat_id = int(query.data.split("|")[1])
    except:
        chat_id = query.message.chat.id

    if hasattr(config, "EQ_CHATS") and chat_id in config.EQ_CHATS:
        config.EQ_CHATS.remove(chat_id)
    
    # Iske baad wala kaam (wapas normal panel lana) aapki callback.py karegi,
    # Isliye yahan hum bas list update karke Continue(False) karenge taki dusre handlers bhi chal sake.
    query.continue_propagation()
