import asyncio
from pyrogram.errors import FloodWait, MessageNotModified

async def stream_typewriter_rich_message(client, chat_id, full_html, chunk_delay=0.08):
    """
    Simulates a typewriter effect for messages.
    """
    # Ek initial message bhejte hain
    msg = await client.send_message(chat_id, "🔄 Loading...")
    await asyncio.sleep(0.2)
    
    # HTML format ko line-by-line show karne ka logic
    lines = full_html.strip().split('\n')
    text_so_far = ""
    
    for line in lines:
        text_so_far += line + "\n"
        try:
            # Har nayi line add karke message edit karega
            if text_so_far.strip():
                await msg.edit_text(text_so_far, disable_web_page_preview=True)
                await asyncio.sleep(chunk_delay)
        except MessageNotModified:
            continue
        except FloodWait as e:
            await asyncio.sleep(e.value)
        except Exception:
            # Agar aadhi HTML tag ki wajah se error aaye (jaise <b> bina close huye), toh usko ignore karke next line pe jayega
            pass
            
    # Final step: Pura complete aur sahi HTML update karna
    try:
        await msg.edit_text(full_html, disable_web_page_preview=True)
    except Exception as e:
        print(f"Typewriter Edit Error: {e}")
