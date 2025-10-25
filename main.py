import os
import sys
import logging

# Setup logging immediately dengan output ke stdout
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

logger.info("🚀 ===== BOT STARTING =====")

try:
    API_ID = int(os.getenv('API_ID', '27037133'))
    API_HASH = os.getenv('API_HASH', '0698732c74d471bca5b7fbba076c52b7')
    SESSION_STRING = os.getenv('SESSION_STRING')
    
    logger.info(f"🔧 API_ID: {API_ID}")
    logger.info(f"🔧 API_HASH: {API_HASH[:10]}***")  # Hide full hash for security
    logger.info(f"🔧 SESSION_STRING: {'***' + SESSION_STRING[-10:] if SESSION_STRING else 'NOT SET'}")
    
    if not SESSION_STRING:
        logger.error("❌ SESSION_STRING environment variable is required!")
        sys.exit(1)
        
except Exception as e:
    logger.error(f"❌ INIT ERROR: {e}")
    sys.exit(1)

# =========================
# KODE USERBOT ASLI
# =========================
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.functions.messages import ForwardMessagesRequest, EditChatTitleRequest
from telethon.tl.functions.channels import EditTitleRequest, EditPhotoRequest, GetParticipantRequest
from telethon.tl.types import Channel, InputChatUploadedPhoto
import json, asyncio, time

logger.info("📦 Importing Telethon modules...")

# Initialize client dengan session string
try:
    client = TelegramClient(
        StringSession(SESSION_STRING), 
        API_ID, 
        API_HASH,
        connection_retries=5,
        timeout=30
    )
    logger.info("✅ Telegram client initialized with SESSION STRING")
except Exception as e:
    logger.error(f"❌ Failed to initialize client: {e}")
    sys.exit(1)

DATA_FILE = "userbot_data.json"

# =========================
# DATABASE SEDERHANA
# =========================
def load_data():
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as f:
                return json.load(f)
    except:
        pass
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
        logger.info(f"✅ Bot started for user: {me.first_name} (ID: {me.id})")
        
        # Kirim pesan start ke saved messages
        try:
            await client.send_message('me', f"🤖 **Bot Started Successfully!**\n\n"
                                          f"• **Platform**: Railway\n"
                                          f"• **Time**: {time.ctime()}\n"
                                          f"• **User**: {me.first_name}\n"
                                          f"• **ID**: {me.id}\n"
                                          f"• **Mode**: SESSION STRING")
            logger.info("✅ Startup message sent to saved messages")
        except Exception as msg_error:
            logger.warning(f"⚠️ Could not send startup message: {msg_error}")
            
    except Exception as e:
        logger.error(f"❌ Failed to initialize owner: {e}")
        raise

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
        me = await client.get_me()
        status_text = f"""
🖥 **USERBOT STATUS**
• **Platform**: Railway
• **Python**: {sys.version.split()[0]}
• **Uptime**: {time.time() - start_time:.0f} detik
• **Mode**: SESSION STRING

✅ **Bot is running on Railway**
📊 **Data tersimpan**: {len([v for v in data.values() if v])} items
👤 **User**: {me.first_name}
🆔 **User ID**: {me.id}
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
            await event.reply("✅ Gambar terkirim!")
        except Exception as e:
            await event.reply(f"⚠️ Gagal mengirim gambar.\nError: {e}")
    else:
        await event.reply("📸 Kamu Belum Menyetting Gambar.\n\nBalas gambar dengan `.p` untuk menyimpan.")

@client.on(events.NewMessage(pattern=r"\.p$", func=lambda e: e.is_reply))
@owner_only
async def simpan_gambar(event):
    reply = await event.get_reply_message()
    if reply and reply.media:
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
        if "wait" in error_msg.lower():
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
    if reply:
        data["tw"] = reply.id
        save_data(data)
        await event.reply("💾 Pesan ini sudah tersimpan untuk .tw")
    else:
        await event.reply("⚠️ Tidak ada pesan yang dibalas.")

@client.on(events.NewMessage(pattern=r"\.tw$"))
@owner_only
async def kirim_tw(event):
    if data.get("tw"):
        try:
            await client(ForwardMessagesRequest(
                from_peer="me", 
                id=[data["tw"]], 
                to_peer=event.chat_id,
                drop_author=True
            ))
            await event.reply("✅ Pesan .tw terkirim!")
        except Exception as e:
            await event.reply(f"⚠️ Gagal mengirim pesan .tw\nError: {e}")
    else:
        await event.reply("🗃️ Tag .tw belum tersimpan di database.\n\nBalas pesan dengan `.tw` untuk menyimpan.")

# =========================
# FITUR: .c
# =========================
@client.on(events.NewMessage(pattern=r"\.c$", func=lambda e: e.is_reply))
@owner_only
async def simpan_c(event):
    reply = await event.get_reply_message()
    if reply:
        data["c"] = reply.id
        save_data(data)
        await event.reply("💾 Pesan ini sudah tersimpan untuk .c")
    else:
        await event.reply("⚠️ Tidak ada pesan yang dibalas.")

@client.on(events.NewMessage(pattern=r"\.c$"))
@owner_only
async def kirim_c(event):
    if data.get("c"):
        try:
            await client(ForwardMessagesRequest(
                from_peer="me", 
                id=[data["c"]], 
                to_peer=event.chat_id,
                drop_author=True
            ))
            await event.reply("✅ Pesan .c terkirim!")
        except Exception as e:
            await event.reply(f"⚠️ Gagal mengirim pesan .c\nError: {e}")
    else:
        await event.reply("🗃️ Tag .c belum tersimpan di database.\n\nBalas pesan dengan `.c` untuk menyimpan.")

# =========================
# FITUR: .lagu
# =========================
@client.on(events.NewMessage(pattern=r"\.lagu$", func=lambda e: e.is_reply))
@owner_only
async def simpan_lagu(event):
    reply = await event.get_reply_message()
    if reply:
        data["lagu"] = reply.id
        save_data(data)
        await event.reply("🎵 Lagu ini sudah tersimpan untuk .lagu")
    else:
        await event.reply("⚠️ Tidak ada pesan yang dibalas.")

@client.on(events.NewMessage(pattern=r"\.lagu$"))
@owner_only
async def kirim_lagu(event):
    if data.get("lagu"):
        try:
            await client(ForwardMessagesRequest(
                from_peer="me", 
                id=[data["lagu"]], 
                to_peer=event.chat_id,
                drop_author=True
            ))
            await event.reply("✅ Lagu terkirim!")
        except Exception as e:
            await event.reply(f"⚠️ Gagal mengirim lagu.\nError: {e}")
    else:
        await event.reply("🗃️ Tag .lagu belum tersimpan di database.\n\nBalas lagu dengan `.lagu` untuk menyimpan.")

# =========================
# FITUR: .sharegrup
# =========================
@client.on(events.NewMessage(pattern=r"\.sharegrup$", func=lambda e: e.is_reply))
@owner_only
async def share_to_all_groups(event):
    reply = await event.get_reply_message()
    if not reply:
        await event.reply("⚠️ Balas pesan yang ingin di-share.")
        return
        
    sent_count = 0
    error_count = 0
    processing_msg = await event.reply("🔄 Memproses broadcast ke semua grup...")
    
    async for dialog in client.iter_dialogs():
        if dialog.is_group:
            try:
                await client.send_message(dialog.id, reply)
                sent_count += 1
                await asyncio.sleep(2)  # Delay untuk hindari spam
            except Exception as e:
                error_count += 1
                logger.error(f"Gagal kirim ke {dialog.name}: {e}")
    
    await processing_msg.delete()
    await event.reply(f"📢 **Broadcast Complete!**\n✅ Berhasil: {sent_count} grup\n❌ Gagal: {error_count} grup")

# =========================
# FITUR: .fitur
# =========================
@client.on(events.NewMessage(pattern=r"\.fitur$"))
async def fitur_list(event):
    fitur_text = """
🤖 **Daftar Fitur Userbot:**

📸 **Gambar & Media**
• `.p` — Kirim gambar tersimpan
• `.p` (reply gambar) — Simpan/ubah gambar
• `.ppgb` — Ganti foto profil grup sesuai gambar di .p

💬 **Pesan Tersimpan**
• `.tw` — Kirim pesan tersimpan
• `.tw` (reply pesan) — Simpan pesan .tw
• `.c` — Kirim pesan tersimpan  
• `.c` (reply pesan) — Simpan pesan .c
• `.lagu` — Kirim lagu tersimpan
• `.lagu` (reply lagu) — Simpan lagu
• `.r <key>` — Kirim pesan tersimpan (key: p, tw, c, lagu)

👥 **Manajemen Grup**
• `.u <nama>` — Ubah nama grup langsung
• `.sharegrup` (reply pesan) — Broadcast ke semua grup

ℹ️ **Info & Status**
• `.status` — Lihat status server
• `.fitur` — Lihat semua fitur bot

🔐 **Hanya untuk owner bot**
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
        await client(ForwardMessagesRequest(
            from_peer="me", 
            id=[pesan_id], 
            to_peer=event.chat_id,
            drop_author=True
        ))
        await event.reply(f"✅ Pesan .{key} terkirim!")
    except Exception as e:
        await event.reply(f"⚠️ Gagal mengirim pesan .{key}\nError: {e}")

# =========================
# FITUR BARU: .ppgb
# =========================
@client.on(events.NewMessage(pattern=r"\.ppgb$"))
@owner_only
async def ganti_profil_grup(event):
    if not data.get("p"):
        await event.reply("📸 Gambar profil grup belum disimpan di .p\n\nGunakan `.p` (reply gambar) dulu untuk menyimpan gambar.")
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
            except Exception as admin_error:
                await event.reply("⚠️ Bot harus menjadi admin dengan hak ubah info untuk mengganti foto grup")
                return

            # Upload dan ganti foto untuk supergroup/channel
            file = await client.upload_file(file_path)
            await client(EditPhotoRequest(channel=entity, photo=InputChatUploadedPhoto(file)))
            await event.reply("✅ Profil grup berhasil diganti!")
        
        else:
            # Untuk grup biasa
            try:
                await client.send_file(entity, file_path, caption="🔄 Mengganti foto grup...")
                await event.reply("✅ Foto grup berhasil diupdate!")
            except Exception as e2:
                await event.reply(f"⚠️ Gagal mengganti profil grup: {e2}")

    except Exception as e:
        await event.reply(f"⚠️ Gagal mengganti profil grup\nError: {e}")

# =========================
# BASIC TEST COMMANDS
# =========================
@client.on(events.NewMessage(pattern=r'\.ping'))
async def ping_handler(event):
    await event.reply('🏓 Pong!')

@client.on(events.NewMessage(pattern=r'\.help'))
async def help_handler(event):
    help_text = """
🤖 **Basic Commands:**
• `.ping` - Test bot response
• `.status` - Bot status
• `.help` - This message
• `.fitur` - All features
"""
    await event.reply(help_text)

# =========================
# KEEP ALIVE & START BOT
# =========================
start_time = time.time()

async def keep_alive():
    while True:
        try:
            me = await client.get_me()
            logger.info(f"💚 Bot is alive - {me.first_name}")
            await asyncio.sleep(300)
        except Exception as e:
            logger.error(f"Keep alive error: {e}")
            await asyncio.sleep(60)

async def main():
    logger.info("🤖 Starting main function...")
    
    try:
        # Test connection first
        logger.info("🔐 Testing connection...")
        await client.start()
        logger.info("✅ Connected to Telegram!")
        
        await init_owner()
        
        # Start keep alive
        asyncio.create_task(keep_alive())
        
        logger.info("🎉 Bot is ready! Waiting for messages...")
        
        await client.run_until_disconnected()
        
    except Exception as e:
        logger.error(f"❌ Fatal error in main: {e}")
        sys.exit(1)

if __name__ == '__main__':
    try:
        # Create event loop properly
        if sys.platform == 'win32':
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
        
    except KeyboardInterrupt:
        logger.info("⏹️ Bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
    finally:
        logger.info("🔴 Bot stopped")
