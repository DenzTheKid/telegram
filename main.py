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

# =========================
# IMPORT UNTUK FITUR .genqr (FIXED)
# =========================
import qrcode
from io import BytesIO

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
# FITUR BARU: .ppgb - VERSI LENGKAP UNTUK GRUP BIASA
# =========================
@client.on(events.NewMessage(pattern=r"\.ppgb$"))
@owner_only
async def ganti_profil_grup(event):
    if not data.get("p"):
        await event.reply("📸 Gambar profil grup belum disimpan di .p\n\nGunakan `.p` (reply gambar) dulu untuk menyimpan gambar.")
        return
    
    try:
        processing_msg = await event.reply("🔄 Mengganti foto profil grup...")
        
        entity = await client.get_entity(event.chat_id)
        file_path = data["p"]

        # Cek apakah file exists
        if not os.path.exists(file_path):
            await processing_msg.edit("❌ File gambar tidak ditemukan! Simpan ulang gambar dengan `.p`")
            return

        # METHOD 1: Untuk semua jenis grup
        try:
            # Upload file
            uploaded_file = await client.upload_file(file_path)
            
            # Coba method EditChatPhoto untuk grup biasa
            from telethon.tl.functions.messages import EditChatPhotoRequest
            from telethon.tl.types import InputChatUploadedPhoto
            
            await client(EditChatPhotoRequest(
                chat_id=entity.id,
                photo=InputChatUploadedPhoto(
                    file=uploaded_file,
                    video=None,
                    video_start_ts=None
                )
            ))
            await processing_msg.edit("✅ Foto profil grup berhasil diganti! (Method 1)")
            return
            
        except Exception as e1:
            logger.warning(f"Method 1 failed: {e1}")
            
            # METHOD 2: Untuk supergroup/channel
            try:
                if isinstance(entity, Channel):
                    # Cek admin rights
                    try:
                        participant = await client(GetParticipantRequest(
                            channel=entity,
                            participant='me'
                        ))
                        admin_rights = getattr(participant.participant, 'admin_rights', None)
                        if not admin_rights or not getattr(admin_rights, 'change_info', False):
                            await processing_msg.edit("⚠️ Bot harus menjadi admin dengan hak **ubah info** untuk mengganti foto grup")
                            return
                    except Exception as admin_error:
                        await processing_msg.edit("⚠️ Bot harus menjadi admin dengan hak **ubah info** untuk mengganti foto grup")
                        return

                    # Upload dan ganti foto
                    file = await client.upload_file(file_path)
                    await client(EditPhotoRequest(
                        channel=entity,
                        photo=InputChatUploadedPhoto(file=file)
                    ))
                    await processing_msg.edit("✅ Foto profil grup berhasil diganti! (Method 2)")
                    return
                else:
                    raise Exception("Not a channel")
                    
            except Exception as e2:
                logger.warning(f"Method 2 failed: {e2}")
                
                # METHOD 3: Cara manual fallback
                try:
                    sent_msg = await client.send_file(
                        entity,
                        file_path,
                        caption="📸 **Foto untuk profil grup**\n\nAdmin silakan gunakan foto ini untuk mengganti foto profil grup secara manual."
                    )
                    await client.pin_message(entity, sent_msg)
                    await processing_msg.edit(
                        "📝 **Foto telah dikirim dan dipin!**\n\n"
                        "Admin silakan:\n"
                        "1. Download foto ini\n"
                        "2. Pergi ke **Info Grup**\n"
                        "3. Pilih **Edit** → **Ganti Foto Grup**\n"
                        "4. Pilih foto yang sudah didownload\n\n"
                        "⚠️ **Note:** Untuk grup biasa, bot memerlukan hak admin lengkap untuk mengganti foto otomatis."
                    )
                    
                except Exception as e3:
                    await processing_msg.edit(f"❌ Semua method gagal:\n• Method 1: {e1}\n• Method 2: {e2}\n• Method 3: {e3}")

    except Exception as e:
        await event.reply(f"❌ Error sistem: {str(e)}")

# =========================
# FITUR CHECK: .checkadmin
# =========================
@client.on(events.NewMessage(pattern=r"\.checkadmin$"))
@owner_only
async def check_admin_rights(event):
    try:
        entity = await client.get_entity(event.chat_id)
        me = await client.get_me()
        
        check_msg = await event.reply("🔍 Checking admin permissions...")
        
        info_text = f"""
👥 **Group Info:**
• **Type**: {'Channel' if isinstance(entity, Channel) else 'Group'}
• **Title**: {getattr(entity, 'title', 'N/A')}
• **ID**: {entity.id}

🤖 **Bot Info:**
• **Name**: {me.first_name}
• **ID**: {me.id}
"""

        # Check if bot is admin
        try:
            if isinstance(entity, Channel):
                participant = await client(GetParticipantRequest(
                    channel=entity,
                    participant='me'
                ))
                admin_rights = getattr(participant.participant, 'admin_rights', None)
                
                if admin_rights:
                    rights_info = f"""
✅ **Bot is ADMIN with rights:**
• Change Info: {getattr(admin_rights, 'change_info', False)}
• Post Messages: {getattr(admin_rights, 'post_messages', False)}
• Edit Messages: {getattr(admin_rights, 'edit_messages', False)}
• Delete Messages: {getattr(admin_rights, 'delete_messages', False)}
• Ban Users: {getattr(admin_rights, 'ban_users', False)}
• Invite Users: {getattr(admin_rights, 'invite_users', False)}
• Pin Messages: {getattr(admin_rights, 'pin_messages', False)}
"""
                    await check_msg.edit(info_text + rights_info)
                else:
                    await check_msg.edit(info_text + "\n❌ **Bot is NOT admin**")
            else:
                # Untuk grup biasa, cek dengan cara lain
                try:
                    # Coba akses admin functionality
                    await client.get_permissions(entity, me)
                    await check_msg.edit(info_text + "\n✅ **Bot has admin access (Basic Group)**")
                except:
                    await check_msg.edit(info_text + "\n❌ **Bot is NOT admin or limited access**")
                    
        except Exception as admin_error:
            await check_msg.edit(info_text + f"\n❌ **Admin check failed**: {admin_error}")
            
    except Exception as e:
        await event.reply(f"❌ Check error: {e}")

# =========================
# FITUR DEBUG: .debug
# =========================
@client.on(events.NewMessage(pattern=r"\.debug$"))
@owner_only
async def debug_info(event):
    try:
        entity = await client.get_entity(event.chat_id)
        
        debug_text = f"""
🔧 **DEBUG INFO**
• **Chat Type**: {'Channel' if isinstance(entity, Channel) else 'Group'}
• **Chat ID**: {entity.id}
• **Title**: {getattr(entity, 'title', 'N/A')}
• **Username**: {getattr(entity, 'username', 'N/A')}
• **Broadcast**: {getattr(entity, 'broadcast', 'N/A')}
• **Megagroup**: {getattr(entity, 'megagroup', 'N/A')}

**File Info:**
• **Saved Image**: {data.get('p', 'None')}
• **File Exists**: {os.path.exists(data.get('p', '')) if data.get('p') else 'No file'}
"""
        msg = await event.reply(debug_text)
        
        # Cek admin rights
        try:
            if isinstance(entity, Channel):
                participant = await client(GetParticipantRequest(
                    channel=entity,
                    participant='me'
                ))
                admin_rights = getattr(participant.participant, 'admin_rights', None)
                if admin_rights:
                    rights_info = f"""
**Admin Rights:**
• Change Info: {getattr(admin_rights, 'change_info', False)}
• Post Messages: {getattr(admin_rights, 'post_messages', False)}
• Edit Messages: {getattr(admin_rights, 'edit_messages', False)}
• Delete Messages: {getattr(admin_rights, 'delete_messages', False)}
• Ban Users: {getattr(admin_rights, 'ban_users', False)}
• Invite Users: {getattr(admin_rights, 'invite_users', False)}
• Pin Messages: {getattr(admin_rights, 'pin_messages', False)}
"""
                    await msg.edit(debug_text + rights_info)
        except Exception as admin_error:
            await msg.edit(debug_text + f"\n**Admin Check Failed**: {admin_error}")
            
    except Exception as e:
        await event.reply(f"❌ Debug error: {e}")

# =========================
# FITUR CLEAN: .clean
# =========================
@client.on(events.NewMessage(pattern=r"\.clean$"))
@owner_only
async def clean_data(event):
    try:
        global data
        data = {"p": None, "tw": None, "c": None, "lagu": None}
        save_data(data)
        await event.reply("🧹 **Data berhasil dibersihkan!**\n\nSemua data tersimpan telah direset.")
    except Exception as e:
        await event.reply(f"❌ Gagal membersihkan data: {e}")

# =========================
# FITUR INFO: .info
# =========================
@client.on(events.NewMessage(pattern=r"\.info$"))
@owner_only
async def info_data(event):
    try:
        info_text = """
💾 **Data Tersimpan:**

"""
        for key, value in data.items():
            status = "✅ Tersimpan" if value else "❌ Kosong"
            info_text += f"• **.{key}**: {status}\n"
        
        info_text += f"\n📁 **Total file**: {len([v for v in data.values() if v])}/4"
        await event.reply(info_text)
    except Exception as e:
        await event.reply(f"❌ Gagal menampilkan info: {e}")

# =========================
# FITUR CARI LAGU: .song
# =========================
@client.on(events.NewMessage(pattern=r"\.song (.+)"))
@owner_only
async def search_song(event):
    try:
        query = event.pattern_match.group(1).strip()
        if not query:
            await event.reply("❌ Masukkan judul lagu yang ingin dicari.\nContoh: `.song coldplay adventure of a lifetime`")
            return

        processing_msg = await event.reply(f"🔍 Mencari lagu: **{query}**...")
        
        # Simple YouTube search without external dependencies
        try:
            import urllib.parse
            
            # Create YouTube search URL
            search_url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}"
            
            song_list = f"🎵 **Hasil Pencarian Lagu:**\n\n"
            song_list += f"**Kata kunci:** {query}\n\n"
            
            # Provide direct YouTube search link
            song_list += "🔍 **Cari di YouTube:**\n"
            song_list += f"• [Buka YouTube Search]({search_url})\n\n"
            
            # Suggest popular search terms
            song_list += "🎧 **Coba kata kunci:**\n"
            song_list += f"• `{query} official audio`\n"
            song_list += f"• `{query} lyrics`\n"
            song_list += f"• `{query} music video`\n"
            song_list += f"• `{query} live`\n\n"
            
            song_list += "💡 **Tips:**\n"
            song_list += "• Copy link YouTube dari hasil pencarian\n"
            song_list += "• Gunakan aplikasi downloader terpisah\n"
            song_list += "• Spotify/Apple Music untuk streaming legal"
            
            await processing_msg.edit(song_list)
            
        except Exception as e:
            await processing_msg.edit(f"❌ Error saat mencari lagu: {str(e)}")
            
    except Exception as e:
        await event.reply(f"❌ Error: {str(e)}")

# =========================
# FITUR CARI LAGU SIMPLE: .music
# =========================
@client.on(events.NewMessage(pattern=r"\.music (.+)"))
@owner_only
async def search_music(event):
    try:
        query = event.pattern_match.group(1).strip()
        if not query:
            await event.reply("❌ Masukkan judul lagu.\nContoh: `.music avicii wake me up`")
            return

        processing_msg = await event.reply(f"🔍 Mencari: **{query}**...")
        
        # Simple music search with suggestions
        import urllib.parse
        
        search_url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query + ' audio')}"
        
        music_results = f"🎵 **Musik untuk '{query}':**\n\n"
        music_results += "**Link pencarian:**\n"
        music_results += f"• [YouTube]({search_url})\n\n"
        
        music_results += "**Lagu populer terkait:**\n"
        music_results += f"• {query} official audio\n"
        music_results += f"• {query} lyrics\n" 
        music_results += f"• {query} instrumental\n"
        music_results += f"• {query} cover version\n\n"
        
        music_results += "🎶 **Streaming legal:**\n"
        music_results += "• Spotify\n• Apple Music\n• YouTube Music\n• SoundCloud"
        
        await processing_msg.edit(music_results)
            
    except Exception as e:
        await event.reply(f"❌ Error: {str(e)}")

# =========================
# FITUR DOWNLOAD LAGU: .dl
# =========================
@client.on(events.NewMessage(pattern=r"\.dl (.+)"))
@owner_only
async def download_song(event):
    try:
        query = event.pattern_match.group(1).strip()
        if not query:
            await event.reply("❌ Masukkan judul lagu yang ingin didownload.\nContoh: `.dl coldplay adventure of a lifetime`")
            return

        processing_msg = await event.reply(f"📥 Mencari dan mendownload: **{query}**...\n⏳ Ini mungkin butuh beberapa saat...")
        
        # Simple method using external service API
        try:
            import urllib.parse
            
            # Search using simple API
            search_query = urllib.parse.quote(query)
            
            download_info = f"🎵 **Download Lagu:** {query}\n\n"
            
            download_info += "🔗 **Alternatif Download:**\n"
            download_info += f"• [YouTube](https://www.youtube.com/results?search_query={search_query}+audio)\n"
            download_info += f"• [Google](https://www.google.com/search?q={search_query}+download+mp3)\n"
            download_info += f"• [SoundCloud](https://soundcloud.com/search?q={search_query})\n\n"
            
            download_info += "💡 **Tips Download Manual:**\n"
            download_info += "1. Cari di YouTube Music\n"
            download_info += "2. Gunakan website converter\n"
            download_info += "3. Aplikasi downloader MP3\n"
            download_info += "4. Streaming platform legal"
            
            await processing_msg.edit(download_info)
            
        except Exception as e:
            await processing_msg.edit(f"❌ Error download: {str(e)}")
            
    except Exception as e:
        await event.reply(f"❌ Error: {str(e)}")

# =========================
# FITUR DOWNLOAD FROM URL: .yt
# =========================
@client.on(events.NewMessage(pattern=r"\.yt (.+)"))
@owner_only
async def download_youtube(event):
    try:
        url = event.pattern_match.group(1).strip()
        
        if not ("youtube.com" in url or "youtu.be" in url):
            await event.reply("❌ Bukan link YouTube yang valid.")
            return
        
        download_msg = await event.reply("📥 Mendownload dari YouTube...\n⏳ Mohon tunggu...")
        
        # Simple method - provide download links
        try:
            import urllib.parse
            
            # Extract video ID
            video_id = None
            if "youtube.com/watch?v=" in url:
                video_id = url.split("youtube.com/watch?v=")[1].split("&")[0]
            elif "youtu.be/" in url:
                video_id = url.split("youtu.be/")[1].split("?")[0]
            
            if video_id:
                download_info = f"🎬 **YouTube Download**\n\n"
                download_info += f"📹 Video ID: `{video_id}`\n\n"
                download_info += "🔗 **Download Links:**\n"
                download_info += f"• [MP3 Download](https://ytmp3.cc/en13/?q=https://youtube.com/watch?v={video_id})\n"
                download_info += f"• [Y2Mate](https://www.y2mate.com/youtube/{video_id})\n"
                download_info += f"• [OnlineConverter](https://www.onlineconverter.com/youtube-to-mp3)\n\n"
                
                download_info += "💡 **Cara Download:**\n"
                download_info += "1. Klik salah satu link di atas\n"
                download_info += "2. Pilih format MP3\n"
                download_info += "3. Download file nya\n"
                download_info += "4. Kirim ke bot dengan `.lagu` (reply audio)"
                
                await download_msg.edit(download_info)
            else:
                await download_msg.edit("❌ Tidak bisa ekstrak Video ID dari link tersebut.")
                
        except Exception as e:
            await download_msg.edit(f"❌ Error: {str(e)}")
            
    except Exception as e:
        await event.reply(f"❌ Error: {str(e)}")

# =========================
# FITUR CARI & DOWNLOAD LAGU: .get
# =========================
@client.on(events.NewMessage(pattern=r"\.get (.+)"))
@owner_only
async def get_song(event):
    try:
        query = event.pattern_match.group(1).strip()
        if not query:
            await event.reply("❌ Masukkan judul lagu.\nContoh: `.get coldplay hymn for the weekend`")
            return

        processing_msg = await event.reply(f"🎵 Mencari: **{query}**...")
        
        import urllib.parse
        encoded_query = urllib.parse.quote(query)
        
        result_text = f"🎵 **Lagu: {query}**\n\n"
        
        result_text += "🔍 **Pencarian Cepat:**\n"
        result_text += f"• [YouTube](https://www.youtube.com/results?search_query={encoded_query}+audio)\n"
        result_text += f"• [YouTube Music](https://music.youtube.com/search?q={encoded_query})\n"
        result_text += f"• [Google](https://www.google.com/search?q={encoded_query}+mp3+download)\n\n"
        
        result_text += "📥 **Download Services:**\n"
        result_text += "• YTMP3.cc\n• Y2Mate.com\n• OnlineVideoConverter.com\n• Convert2MP3.net\n\n"
        
        result_text += "🎧 **Streaming Legal:**\n"
        result_text += "• Spotify\n• Apple Music\n• YouTube Music\n• Deezer\n\n"
        
        result_text += "💡 **Cara Download:**\n"
        result_text += "1. Cari lagu di YouTube\n"
        result_text += "2. Copy link YouTube nya\n"
        result_text += "3. Gunakan `.yt <link>` untuk download\n"
        result_text += "4. Atau gunakan website converter"
        
        await processing_msg.edit(result_text)
            
    except Exception as e:
        await event.reply(f"❌ Error: {str(e)}")

# =========================
# FITUR: .genqr (MANUAL SESSION GUIDE - COMPATIBLE)
# =========================
@client.on(events.NewMessage(pattern=r'\.genqr'))
@owner_only
async def generate_qr_manual(event):
    """Manual guide untuk generate session - Compatible Version"""
    
    guide_text = """
🔐 **CARA GENERATE SESSION UNTUK AKUN BARU:**

**📱 Method 1: Session Generator Script (Recommended)**
1. Buat file `session_generator.py` dengan content berikut:

```python
from telethon.sync import TelegramClient
from telethon.sessions import StringSession

API_ID = 27037133
API_HASH = "0698732c74d471bca5b7fbba076c52b7"

print("📱 Telegram Session Generator")
print("=" * 40)
print("Scan QR code yang muncul...")

with TelegramClient(StringSession(), API_ID, API_HASH) as client:
    client.start()
    session_string = client.session.save()
    me = client.get_me()
    
    print(f"✅ LOGIN BERHASIL!")
    print(f"👤 Name: {me.first_name}")
    print(f"📞 Phone: {me.phone}")
    print(f"🆔 ID: {me.id}")
    print(f"🔐 SESSION STRING:")
    print("=" * 50)
    print(session_string)
    print("=" * 50)
    print(f"💡 Tambahkan sebagai SESSION_2 di Railway!")
