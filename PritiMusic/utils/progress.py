import asyncio
import re
from pyrogram.errors import FloodWait, MessageNotModified
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

async def stream_typewriter_rich_message(client, chat_id, full_html, reply_markup=None, chunk_delay=0.08):
    """
    Simulates a typewriter effect and parses custom <tg-button-row> HTML into Telegram buttons.
    """
    keyboard = []
    
    # 1. Custom Button HTML Parser (Extracts tg-button-row blocks)
    row_pattern = r'<tg-button-row[^>]*>(.*?)</tg-button-row>'
    button_pattern = r'<tg-button\s+type="([^"]+)"(?:[^>]*?(?:url|data)="([^"]+)")?[^>]*>(.*?)</tg-button>'

    # Har ek row ko dhundna
    for row_match in re.finditer(row_pattern, full_html, re.DOTALL):
        row_buttons = []
        # Row ke andar buttons ko dhundna
        for btn_match in re.finditer(button_pattern, row_match.group(1)):
            btn_type, btn_val, btn_text = btn_match.groups()
            if btn_type == "url":
                row_buttons.append(InlineKeyboardButton(btn_text.strip(), url=btn_val))
            elif btn_type == "callback_data":
                row_buttons.append(InlineKeyboardButton(btn_text.strip(), callback_data=btn_val))
        if row_buttons:
            keyboard.append(row_buttons)

    # 2. HTML Text se buttons wala part remove kar dena (taaki text me dikhayi na de)
    clean_html = re.sub(row_pattern, '', full_html, flags=re.DOTALL).strip()
    
    # Final keyboard set karna
    final_markup = InlineKeyboardMarkup(keyboard) if keyboard else reply_markup

    # 3. Typewriter Animation Logic
    msg = await client.send_message(chat_id, "🔄 Loading Baby...")
    await asyncio.sleep(0.2)
    
    lines = clean_html.split('\n')
    text_so_far = ""
    
    for line in lines:
        text_so_far += line + "\n"
        try:
            if text_so_far.strip():
                await msg.edit_text(text_so_far, disable_web_page_preview=True)
                await asyncio.sleep(chunk_delay)
        except MessageNotModified:
            continue
        except FloodWait as e:
            await asyncio.sleep(e.value)
        except Exception:
            pass
            
    # 4. End me pura clean text aur Pyrogram waale buttons lagana
    try:
        await msg.edit_text(clean_html, disable_web_page_preview=True, reply_markup=final_markup)
    except Exception as e:
        print(f"Typewriter Edit Error: {e}")
