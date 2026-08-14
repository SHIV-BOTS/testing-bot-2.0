from pyrogram import filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup

from PritiMusic import LOGGER, app
from PritiMusic.core.call import Lucky
from PritiMusic.utils.inline.play import eq_markup

import config


# Chat-wise volume memory
active_volumes = {}


def get_callback_chat_id(query: CallbackQuery):
    """
    Callback data se action aur chat_id read karta hai.
    Example:
    vol_up|-100123456789
    eq_bass|-100123456789
    """
    data = str(query.data or "").strip()
    action, separator, raw_chat_id = data.partition("|")

    if separator:
        try:
            return action, int(raw_chat_id)
        except (TypeError, ValueError):
            pass

    if query.message and query.message.chat:
        return action, int(query.message.chat.id)

    raise ValueError("Chat ID not found")


def answer_callback_error(query, message):
    """
    Callback error ko safely show karta hai.
    """
    try:
        return query.answer(
            message,
            show_alert=True,
        )
    except Exception:
        return None


# ----------------------------------------------------
# EQUALIZER MENU OPENER
# ----------------------------------------------------
@app.on_callback_query(filters.regex(r"^EQMenu"))
async def eq_menu_callback(
    client,
    query: CallbackQuery,
):
    try:
        action, chat_id = get_callback_chat_id(query)

        if not hasattr(config, "EQ_CHATS"):
            config.EQ_CHATS = []

        if chat_id not in config.EQ_CHATS:
            config.EQ_CHATS.append(chat_id)

        keyboard = InlineKeyboardMarkup(
            eq_markup(
                None,
                chat_id,
            )
        )

        await query.edit_message_reply_markup(
            reply_markup=keyboard,
        )

        await query.answer(
            "Equalizer & Volume Menu Opened",
            show_alert=False,
        )

    except Exception as error:
        LOGGER(__name__).error(
            f"EQ menu error: {error}"
        )

        await answer_callback_error(
            query,
            "Equalizer menu open nahi ho saka.",
        )


# ----------------------------------------------------
# VOLUME CONTROLLER
# ----------------------------------------------------
@app.on_callback_query(filters.regex(r"^vol_"))
async def vol_controls(
    client,
    query: CallbackQuery,
):
    try:
        action, chat_id = get_callback_chat_id(query)

    except Exception as error:
        LOGGER(__name__).error(
            f"Volume callback parse error: {error}"
        )

        return await answer_callback_error(
            query,
            "Invalid volume callback.",
        )

    valid_actions = {
        "vol_up",
        "vol_down",
        "vol_boost",
    }

    if action not in valid_actions:
        return await answer_callback_error(
            query,
            "Invalid volume action.",
        )

    previous_volume = active_volumes.get(
        chat_id,
        100,
    )

    current_volume = previous_volume

    if action == "vol_up":
        current_volume = min(
            current_volume + 50,
            10000,
        )

    elif action == "vol_down":
        current_volume = max(
            current_volume - 20,
            0,
        )

    elif action == "vol_boost":
        current_volume = min(
            current_volume + 500,
            10000,
        )

    active_volumes[chat_id] = current_volume

    try:
        # New fixed Call engine method
        await Lucky.change_volume_call(
            chat_id,
            current_volume,
        )

    except Exception as error:
        # Agar stream active nahi hai to previous value restore karo
        active_volumes[chat_id] = previous_volume

        LOGGER(__name__).error(
            f"Volume update failed in {chat_id}: {error}"
        )

        return await answer_callback_error(
            query,
            "Pehle music play karke voice chat start karein.",
        )

    if current_volume >= 10000:
        message = (
            "MAX BOOST ACTIVATED: 10,000%"
        )

    elif current_volume <= 0:
        message = "MUSIC MUTED: 0%"

    else:
        message = (
            f"VOLUME: {current_volume}%"
        )

    await query.answer(
        message,
        show_alert=True,
    )


# ----------------------------------------------------
# EQUALIZER PRESETS
# ----------------------------------------------------
@app.on_callback_query(filters.regex(r"^eq_"))
async def eq_controls(
    client,
    query: CallbackQuery,
):
    try:
        action, chat_id = get_callback_chat_id(query)

    except Exception as error:
        LOGGER(__name__).error(
            f"Equalizer callback parse error: {error}"
        )

        return await answer_callback_error(
            query,
            "Invalid equalizer callback.",
        )

    action_name = action.replace(
        "eq_",
        "",
        1,
    )

    filters_map = {
        "8d": "apulsator=hz=0.125",
        "auditorium": "aecho=0.8:0.9:1000:0.3",
        "bass": "bass=g=25:f=110:w=0.3",
        "club": "bass=g=15,treble=g=5",
        "dj": "asetrate=44100*1.15,atempo=1.15,bass=g=15:f=110:w=0.6,treble=g=5",
        "slowed": "asetrate=44100*0.85,atempo=0.85,aecho=0.8:0.9:1000:0.3",
        "nightcore": "asetrate=48000*1.25,aresample=48000",
        "normal": "anull",
    }

    if action_name not in filters_map:
        return await answer_callback_error(
            query,
            "Invalid equalizer mode.",
        )

    selected_filter = filters_map[action_name]

    try:
        # New fixed Call engine method
        await Lucky.change_filter(
            chat_id,
            selected_filter,
        )

    except Exception as error:
        LOGGER(__name__).error(
            f"Equalizer update failed in {chat_id}: {error}"
        )

        return await answer_callback_error(
            query,
            "Pehle music play karke voice chat start karein.",
        )

    if action_name in {
        "dj",
        "bass",
        "club",
    }:
        emoji = "DJ"

    else:
        emoji = "EQ"

    await query.answer(
        f"{emoji} Mode Set: {action_name.title()}",
        show_alert=True,
    )


# ----------------------------------------------------
# BACK BUTTON
# ----------------------------------------------------
@app.on_callback_query(
    filters.regex(r"^PanelMarkup None")
)
async def eq_back_handler(
    client,
    query: CallbackQuery,
):
    try:
        action, chat_id = get_callback_chat_id(query)

    except Exception as error:
        LOGGER(__name__).error(
            f"Back callback parse error: {error}"
        )

        return await answer_callback_error(
            query,
            "Invalid back callback.",
        )

    if hasattr(config, "EQ_CHATS"):
        if chat_id in config.EQ_CHATS:
            config.EQ_CHATS.remove(chat_id)

    # Main callback handler ko continue karne deta hai
    query.continue_propagation()
