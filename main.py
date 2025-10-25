import os
import sys
import logging

# Setup logging immediately dengan output ke stdout
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    stream=sys.stdout  # Force output to stdout
)
logger = logging.getLogger(__name__)

# Test logging immediately
logger.info("🚀 ===== BOT STARTING =====")
print("🟢 PRINT: Bot starting...", flush=True)

try:
    # Test environment variables
    API_ID = os.getenv('API_ID')
    API_HASH = os.getenv('API_HASH')
    SESSION_NAME = os.getenv('SESSION_NAME', 'userbot')
    
    logger.info(f"🔧 API_ID: {API_ID}")
    logger.info(f"🔧 API_HASH: {API_HASH}")
    logger.info(f"🔧 SESSION_NAME: {SESSION_NAME}")
    
    if not API_ID or not API_HASH:
        logger.error("❌ MISSING ENVIRONMENT VARIABLES")
        sys.exit(1)
        
    # Convert API_ID to integer
    API_ID = int(API_ID)
    logger.info("✅ Environment variables loaded successfully")
    
except Exception as e:
    logger.error(f"❌ INIT ERROR: {e}")
    sys.exit(1)

# =========================
# KODE USERBOT ASLI
# =========================
from telethon import TelegramClient, events, functions
from telethon.tl.functions.messages import ForwardMessagesRequest, EditChatTitleRequest
from telethon.tl.functions.channels import EditTitleRequest, EditPhotoRequest, GetParticipantRequest
from telethon.tl.types import Channel, InputChatUploadedPhoto, InputPhoto
from telethon.tl.functions.photos import UploadProfilePhotoRequest, DeletePhotosRequest
import json, asyncio, time

logger.info("📦 Importing Telethon modules...")

client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
DATA_FILE = "userbot_data.json"

# =========================
# DATABASE SEDERHANA
# =========================
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except:
            return {"p": None, "tw": None, "c": None, "lagu": None}
    return {"p": None, "tw": None, "c": None, "lagu": None}

def save_data(data):
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving data: {e}")

data = load_data()
OWNER_ID = None

async def init_owner():
    global OWNER_ID
    try:
        me = await client.get_me()
        OWNER_ID = me.id
        logger.info(f"Bot started for user: {me.first_name} (ID: {me.id})")
    except Exception as e:
        logger.error(f"Failed to initialize owner: {e}")

def owner_only(func):
    async def wrapper(event):
        if OWNER_ID is None:
            await event.reply("⚠️ Owner ID belum diinisialisasi.")
            return
        if event.sender_id != OWNER_ID:
            await event.reply("❌ Kamu tidak memiliki izin untuk menggunakan perintah ini.")
            return
        return await func(event)
    return wrapper

# =========================
# FITUR: STATUS SERVER
# =========================
@client.on(events.NewMessage(pattern=r'\.status'))
@owner_only
async def server_status(event):
    try:
        status_text = f"""
🖥 **USERBOT STATUS**
• **Platform**: Railway
• **Python**: {sys.version.split()[0]}
• **Uptime**: {time.time() - start_time:.0f} detik

✅ **Bot is running on Railway**
📊 **Data tersimpan**: {len([v for v in data.values() if v])} items
👤 **Owner ID**: {OWNER_ID}
"""
        await event.reply(status_text)
    except Exception as e:
        await event.reply(f"❌ Error getting status: {e}")

# =========================
# FITUR: .p (GAMBAR TERSIMPAN)
# =========================
@client.on(events.NewMessage(pattern=r"\.p$"))
@owner_only
async def kirim_gambar(event):
    if data.get("p"):
        try:
            await client.send_file(event.chat_id, data["p"])
        except Exception as e:
            await event.reply(f"⚠️ Gagal mengirim gambar.\nError: {e}")
    else:
        await event.reply("📸 Kamu Belum Menyetting Gambar.")

@client.on(events.NewMessage(pattern=r"\.p$", func=lambda e: e.is_reply))
@owner_only
async def simpan_gambar(event):
    reply = await event.get_reply_message()
    if reply.media:
        try:
            # Buat folder downloads jika tidak ada
            if not os.path.exists('downloads'):
                os.makedirs('downloads')
            
            file_path = await reply.download_media(file='downloads/')
            data["p"] = file_path
            save_data(data)
            await event.reply("✅ Gambar berhasil disimpan atau diperbarui.")
        except Exception as e:
            await event.reply(f"⚠️ Gagal menyimpan gambar: {e}")
    else:
        await event.reply("⚠️ Balas gambar untuk disimpan.")

# =========================
# FITUR: .u (UBAH NAMA GRUP)
# =========================
@client.on(events.NewMessage(pattern=r"\.u (.+)"))
@owner_only
async def ubah_nama_grup(event):
    new_name = event.pattern_match.group(1).strip()
    try:
        entity = await client.get_entity(event.chat_id)
        if isinstance(entity, Channel):
            await client(EditTitleRequest(channel=entity, title=new_name))
        else:
            await client(EditChatTitleRequest(chat_id=entity.id, title=new_name))
        await event.reply(f"✅ Nama grup berhasil diganti menjadi **{new_name}**")
    except Exception as e:
        error_msg = str(e)
        if "wait" in error_msg:
            await event.reply("⏰ Terlalu sering mengganti nama! Tunggu beberapa menit.")
        else:
            await event.reply(f"❌ Gagal ubah nama grup: {error_msg}")

# =========================
# FITUR: .tw
# =========================
@client.on(events.NewMessage(pattern=r"\.tw$", func=lambda e: e.is_reply))
@owner_only
async def simpan_tw(event):
    reply = await event.get_reply_message()
    data["tw"] = reply.id
    save_data(data)
    await event.reply("💾 Pesan ini sudah tersimpan untuk .tw")

@client.on(events.NewMessage(pattern=r"\.tw$"))
@owner_only
async def kirim_tw(event):
    if data.get("tw"):
        try:
            await client(ForwardMessagesRequest(from_peer="me", id=[data["tw"]], to_peer=event.chat_id))
        except Exception as e:
            await event.reply(f"⚠️ Gagal mengirim pesan .tw\nError: {e}")
    else:
        await event.reply("🗃️ Tag .tw belum tersimpan di database.")

# =========================
# FITUR: .c
# =========================
@client.on(events.NewMessage(pattern=r"\.c$", func=lambda e: e.is_reply))
@owner_only
async def simpan_c(event):
    reply = await event.get_reply_message()
    data["c"] = reply.id
    save_data(data)
    await event.reply("💾 Pesan ini sudah tersimpan untuk .c")

@client.on(events.NewMessage(pattern=r"\.c$"))
@owner_only
async def kirim_c(event):
    if data.get("c"):
        try:
            await client(ForwardMessagesRequest(from_peer="me", id=[data["c"]], to_peer=event.chat_id))
        except Exception as e:
            await event.reply(f"⚠️ Gagal mengirim pesan .c\nError: {e}")
    else:
        await event.reply("🗃️ Tag .c belum tersimpan di database.")

# =========================
# FITUR: .lagu
# =========================
@client.on(events.NewMessage(pattern=r"\.lagu$", func=lambda e: e.is_reply))
@owner_only
async def simpan_lagu(event):
    reply = await event.get_reply_message()
    data["lagu"] = reply.id
    save_data(data)
    await event.reply("🎵 Lagu ini sudah tersimpan untuk .lagu")

@client.on(events.NewMessage(pattern=r"\.lagu$"))
@owner_only
async def kirim_lagu(event):
    if data.get("lagu"):
        try:
            await client(ForwardMessagesRequest(from_peer="me", id=[data["lagu"]], to_peer=event.chat_id))
        except Exception as e:
            await event.reply(f"⚠️ Gagal mengirim lagu.\nError: {e}")
    else:
        await event.reply("🗃️ Tag .lagu belum tersimpan di database.")

# =========================
# FITUR: .sharegrup
# =========================
@client.on(events.NewMessage(pattern=r"\.sharegrup$", func=lambda e: e.is_reply))
@owner_only
async def share_to_all_groups(event):
    reply = await event.get_reply_message()
    sent_count = 0
    async for dialog in client.iter_dialogs():
        if dialog.is_group:
            try:
                await client.send_message(dialog.id, reply)
                sent_count += 1
                await asyncio.sleep(1)  # Delay untuk hindari spam
            except:
                pass
    await event.reply(f"📢 Pesan berhasil dikirim ke {sent_count} grup!")

# =========================
# FITUR: .fitur
# =========================
@client.on(events.NewMessage(pattern=r"\.fitur$"))
async def fitur_list(event):
    fitur_text = """
🤖 Daftar Fitur Userbot:
• `.p` — Kirim gambar tersimpan
• `.p` (reply gambar) — Simpan / ubah gambar
• `.u <nama>` — Ubah nama grup langsung
• `.tw` — Kirim pesan tersimpan
• `.tw` (reply pesan) — Simpan pesan .tw
• `.c` — Kirim pesan tersimpan
• `.c` (reply pesan) — Simpan pesan .c
• `.lagu` — Kirim lagu tersimpan
• `.lagu` (reply lagu) — Simpan lagu
• `.sharegrup` (reply pesan) — Broadcast ke semua grup
• `.r <key>` — Kirim pesan tersimpan (key: p, tw, c, lagu)
• `.ppgb` — Ganti foto profil grup sesuai gambar di .p
• `.status` — Lihat status server
• `.fitur` — Lihat semua fitur bot
"""
    await event.reply(fitur_text)

# =========================
# FITUR BARU: .r
# =========================
@client.on(events.NewMessage(pattern=r"\.r (\w+)"))
@owner_only
async def kirim_tersimpan(event):
    key = event.pattern_match.group(1).lower()
    pesan_id = data.get(key)
    if not pesan_id:
        await event.reply(f"🗃️ Tidak ada pesan tersimpan untuk .{key}")
        return
    try:
        await client(ForwardMessagesRequest(from_peer="me", id=[pesan_id], to_peer=event.chat_id))
    except Exception as e:
        await event.reply(f"⚠️ Gagal mengirim pesan .{key}\nError: {e}")

# =========================
# FITUR BARU: .ppgb
# =========================
@client.on(events.NewMessage(pattern=r"\.ppgb$"))
@owner_only
async def ganti_profil_grup(event):
    if not data.get("p"):
        await event.reply("📸 Gambar profil grup belum disimpan di .p")
        return
    
    try:
        entity = await client.get_entity(event.chat_id)
        file_path = data["p"]

        if isinstance(entity, Channel):
            # Cek admin rights
            try:
                participant = await client(GetParticipantRequest(
                    channel=entity,
                    participant='me'
                ))
                if not getattr(participant.participant, 'admin_rights', None):
                    await event.reply("⚠️ Bot harus menjadi admin dengan hak ubah info untuk mengganti foto grup")
                    return
            except:
                await event.reply("⚠️ Bot harus menjadi admin dengan hak ubah info untuk mengganti foto grup")
                return

            # Upload dan ganti foto untuk supergroup/channel
            file = await client.upload_file(file_path)
            await client(EditPhotoRequest(channel=entity, photo=InputChatUploadedPhoto(file)))
            await event.reply("✅ Profil grup berhasil diganti!")
        
        else:
            # Untuk grup biasa - method alternatif
            try:
                uploaded_file = await client.upload_file(file_path)
                result = await client(UploadProfilePhotoRequest(file=uploaded_file))
                
                input_photo = InputPhoto(
                    id=result.photo.id,
                    access_hash=result.photo.access_hash,
                    file_reference=result.photo.file_reference
                )
                
                from telethon.tl.functions.messages import EditChatPhotoRequest
                await client(EditChatPhotoRequest(
                    chat_id=entity.id,
                    photo=input_photo
                ))
                
                # Hapus foto dari profil kita
                await client(DeletePhotosRequest(id=[result.photo]))
                
                await event.reply("✅ Profil grup berhasil diganti!")
            except Exception as e2:
                await event.reply(f"⚠️ Gagal mengganti profil grup: {e2}")

    except Exception as e:
        await event.reply(f"⚠️ Gagal mengganti profil grup\nError: {e}")

# =========================
# KEEP ALIVE & START BOT
# =========================
start_time = time.time()

async def keep_alive():
    while True:
        try:
            me = await client.get_me()
            logger.info(f"Bot is alive - {me.first_name}")
            await asyncio.sleep(300)  # Check every 5 minutes
        except Exception as e:
            logger.error(f"Keep alive error: {e}")
            await asyncio.sleep(60)

async def main():
    logger.info("🤖 Initializing Telegram client...")
    
    # Buat folder downloads jika tidak ada
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
    
    try:
        await client.start()
        logger.info("✅ Telegram client started successfully")
        
        await init_owner()
        
        # Start keep alive task
        asyncio.create_task(keep_alive())
        
        logger.info("🎉 Userbot started successfully on Railway!")
        logger.info("💚 Bot will stay online 24/7")
        
        await client.run_until_disconnected()
        
    except Exception as e:
        logger.error(f"❌ Failed to start bot: {e}")
        sys.exit(1)

if __name__ == '__main__':
    logger.info("🚀 Starting main function...")
    client.loop.run_until_complete(main())
