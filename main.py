import os
import sys
import logging
from datetime import datetime

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
# VARIABEL UNTUK STOP SHARE PM
# =========================
stop_share_pm = False  # Flag untuk menghentikan broadcast PM

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
# FITUR BARU: .rekap - UNTUK MENGHITUNG FEE OTOMATIS
# =========================
@client.on(events.NewMessage(pattern=r"\.rekap(?:\s+([\d.]+))?$"))
@owner_only
async def calculate_fee(event):
    """Menghitung fee berdasarkan persentase yang diberikan"""
    try:
        # Default persentase 5.5% jika tidak diberikan
        persen_input = event.pattern_match.group(1)
        if persen_input:
            try:
                persentase = float(persen_input)
                if persentase <= 0 or persentase >= 100:
                    await event.reply("❌ Persentase harus antara 0.1 sampai 99.9")
                    return
            except ValueError:
                await event.reply("❌ Format persentase salah! Contoh: `.rekap 5.5`")
                return
        else:
            persentase = 5.5  # Default 5.5%

        processing_msg = await event.reply(f"🔄 Menghitung fee dengan {persentase}%...")

        # DATA AWAL - BISA DIUBAH SESUKA HATI!
        # Type: "P" atau "LF" = sama artinya, "" = tanpa P/LF
        data_B = {  # TIM B
            "EL": {"nominal": 10, "type": "P"},
            "COLI": {"nominal": 40, "type": "P"},
            "EDI": {"nominal": 18, "type": "P"},
            "TONI": {"nominal": 18, "type": "P"},
            "DZ": {"nominal": 20, "type": "P"},
            "MADA": {"nominal": 12, "type": "P"},
            "YANZ": {"nominal": 15, "type": ""},
            "TAT": {"nominal": 50, "type": ""},
            "FERX": {"nominal": 120, "type": "P"},
            "DUNZ": {"nominal": 5, "type": "P"},
            "RAUL": {"nominal": 40, "type": "P"}
        }

        data_K = {  # TIM K
            "VIS": {"nominal": 78, "type": "P"},
            "REZA": {"nominal": 125, "type": "P"},
            "SAS": {"nominal": 4, "type": "P"},
            "KRISNA": {"nominal": 50, "type": "P"},
            "PEMULA": {"nominal": 15, "type": "P"},
            "TRUTA": {"nominal": 31, "type": "P"},
            "HAHA": {"nominal": 5, "type": ""},
            "IYAN": {"nominal": 10, "type": "P"},
            "MAL": {"nominal": 30, "type": "P"}
        }

        # Fungsi untuk menghitung hasil
        def hitung_fee(nominal, tipe, persen):
            if tipe == "P" or tipe == "LF":  # Ada tulisan P atau LF
                # nominal - persen%
                fee = nominal - (nominal * persen / 100)
                return round(fee)
            else:  # Tidak ada P/LF
                # nominal × (persentase × 2)%
                fee = nominal * (persen * 2 / 100)
                return round(fee)

        # Proses perhitungan untuk Tim B
        hasil_B = []
        total_fee_B = 0
        
        for nama, data in data_B.items():
            nominal = data["nominal"]
            tipe = data["type"]
            hasil = hitung_fee(nominal, tipe, persentase)
            hasil_B.append((nama, nominal, hasil, tipe))
            # SEMUA MASUK TOTAL FEE (baik yang P/LF maupun tanpa P/LF)
            total_fee_B += hasil

        # Proses perhitungan untuk Tim K
        hasil_K = []
        total_fee_K = 0
        
        for nama, data in data_K.items():
            nominal = data["nominal"]
            tipe = data["type"]
            hasil = hitung_fee(nominal, tipe, persentase)
            hasil_K.append((nama, nominal, hasil, tipe))
            # SEMUA MASUK TOTAL FEE (baik yang P/LF maupun tanpa P/LF)
            total_fee_K += hasil

        # Format output
        output = f"📊 **REKAP FEE - {persentase}%**\n\n"
        
        # Bagian B
        output += "**B:**\n"
        for nama, nominal, hasil, tipe in hasil_B:
            type_indicator = "p" if tipe == "P" or tipe == "LF" else " "
            output += f"{nama} {nominal} // {hasil} {type_indicator}\n"
        
        output += "\n**K:**\n"
        for nama, nominal, hasil, tipe in hasil_K:
            type_indicator = "p" if tipe == "P" or tipe == "LF" else " "
            output += f"{nama} {nominal} // {hasil} {type_indicator}\n"
        
        # Total fee
        output += f"\n🎉 **Total fee yang Anda dapat dari B adalah: {total_fee_B} selamat!** 🎉\n"
        output += f"🎉 **Total fee yang Anda dapat dari K adalah: {total_fee_K} selamat!** 🎉\n\n"
        
        output += f"💡 **Keterangan:**\n"
        output += f"• **P/LF**: nominal - {persentase}%\n"
        output += f"• **Tanpa P/LF**: nominal × {persentase * 2}%\n"
        output += "━━━━━━━━━━━━━━━━━━\n"
        output += "🤖 Bot by denz | @denzwel1"

        await processing_msg.edit(output)

    except Exception as e:
        await event.reply(f"❌ Error menghitung fee: {str(e)}")

# =========================
# FITUR BARU: .setrekap - UNTUK MENGUBAH DATA REKAP
# =========================
@client.on(events.NewMessage(pattern=r"\.setrekap$"))
@owner_only
async def set_rekap_data(event):
    """Petunjuk untuk mengubah data rekap"""
    help_text = """
📝 **CARA MENGUBAH DATA REKAP:**

Untuk mengubah data rekap, Anda perlu mengedit langsung di kode bot:

1. **Cari fungsi `calculate_fee`** di kode
2. **Edit dictionary `data_B` dan `data_K`**
3. **Format data:**
   ```python
   "NAMA": {"nominal": 100, "type": "P"}   # Dengan P
   "NAMA": {"nominal": 100, "type": "LF"}  # Dengan LF  
   "NAMA": {"nominal": 100, "type": ""}    # Tanpa P/LF

# =========================
# FITUR BARU: .sharepm - BROADCAST KE SEMUA PRIVATE CHAT
# =========================
@client.on(events.NewMessage(pattern=r"\.sharepm$", func=lambda e: e.is_reply))
@owner_only
async def share_to_all_private_chats(event):
    """Broadcast pesan ke semua chat private/personal"""
    global stop_share_pm
    
    # Reset stop flag
    stop_share_pm = False
    
    reply = await event.get_reply_message()
    if not reply:
        await event.reply("⚠️ Balas pesan yang ingin di-share ke semua private chat.")
        return
        
    processing_msg = await event.reply("🔄 Memproses broadcast ke semua private chat...\n\n⏹️ **Gunakan `.stopsharepm` untuk menghentikan broadcast**")
    
    sent_count = 0
    error_count = 0
    skipped_count = 0
    
    async for dialog in client.iter_dialogs():
        # Cek jika stop flag diaktifkan
        if stop_share_pm:
            await processing_msg.edit(f"🛑 **BROADCAST DIHENTIKAN!**\n\n📊 **Progress Sebelum Berhenti:**\n✅ Berhasil: {sent_count}\n❌ Gagal: {error_count}\n⏭️ Dilewati: {skipped_count}")
            return
            
        try:
            # Hanya kirim ke chat personal/private (bukan grup/channel)
            if dialog.is_user and not dialog.entity.bot:  # Skip bot
                try:
                    await client.send_message(dialog.id, reply)
                    sent_count += 1
                    await asyncio.sleep(1)  # Delay untuk hindari spam
                    
                    # Update progress setiap 5 pesan
                    if sent_count % 5 == 0:
                        await processing_msg.edit(f"🔄 Mengirim ke private chat...\n\n⏹️ **Gunakan `.stopsharepm` untuk menghentikan**\n\n✅ Berhasil: {sent_count}\n❌ Gagal: {error_count}\n⏭️ Dilewati: {skipped_count}")
                        
                except Exception as e:
                    error_count += 1
                    logger.warning(f"Gagal kirim ke {dialog.name}: {e}")
                    
        except Exception as e:
            skipped_count += 1
            continue
    
    # Final report
    report_msg = f"""
📨 **BROADCAST PRIVATE CHAT COMPLETE**

📊 **Hasil:**
✅ **Berhasil**: {sent_count} chat
❌ **Gagal**: {error_count} chat  
⏭️ **Dilewati**: {skipped_count} chat

💡 **Catatan:**
• Hanya mengirim ke chat personal/private
• Bot otomatis dilewati
• Delay 1 detik antar pesan untuk hindari spam

━━━━━━━━━━━━━━━━━━
🤖 Bot by denz | @denzwel1
"""
    
    await processing_msg.edit(report_msg)
    
    # Kirim juga laporan ke saved messages
    await client.send_message('me', f"📨 Broadcast PM selesai:\nBerhasil: {sent_count}\nGagal: {error_count}\nDilewati: {skipped_count}")

# =========================
# FITUR BARU: .stopsharepm - UNTUK MENGENTIKAN BROADCAST PM
# =========================
@client.on(events.NewMessage(pattern=r"\.stopsharepm$"))
@owner_only
async def stop_share_pm_command(event):
    """Menghentikan broadcast PM yang sedang berjalan"""
    global stop_share_pm
    
    if stop_share_pm:
        await event.reply("⚠️ Tidak ada broadcast PM yang sedang berjalan.")
        return
        
    stop_share_pm = True
    await event.reply("🛑 **Perintah berhenti diterima!**\n\nBroadcast PM akan dihentikan setelah pesan saat ini selesai dikirim.")
    
    logger.info("🛑 Stop share PM command received")

# =========================
# FITUR: NOTIFIKASI BOT DITAMBAHKAN KE GRUP (IMPROVED VERSION)
# =========================
@client.on(events.ChatAction)
async def chat_action_handler(event):
    try:
        logger.info(f"🔍 ChatAction event detected: {event}")
        
        # Cek jika ada user yang ditambahkan
        if event.user_added:
            added_users = await event.get_users()
            me = await client.get_me()
            
            # Cek jika bot yang ditambahkan
            if any(user.id == me.id for user in added_users):
                try:
                    added_by_user = await event.get_user()
                    adder_name = f"{added_by_user.first_name or ''} {added_by_user.last_name or ''}".strip()
                    adder_username = f"@{added_by_user.username}" if added_by_user.username else "Tidak ada username"
                    adder_id = added_by_user.id
                except:
                    adder_name = "Unknown"
                    adder_username = "Tidak diketahui"
                    adder_id = "Unknown"
                
                chat = await event.get_chat()
                
                # Informasi tentang grup
                chat_title = getattr(chat, 'title', 'Unknown Group')
                chat_id = chat.id
                chat_username = f"@{chat.username}" if getattr(chat, 'username', None) else "Tidak ada username"
                
                # Hitung jumlah member
                try:
                    participants_count = await client.get_participants(chat, limit=0)
                    member_count = len(participants_count)
                except:
                    member_count = "Tidak bisa dihitung"
                
                # Waktu saat ini
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # Buat pesan notifikasi
                notification_msg = f"""
🔔 **BOT DITAMBAHKAN KE GRUP BARU**

👤 **Ditambahkan oleh:**
• **Nama**: {adder_name}
• **Username**: {adder_username}
• **ID**: `{adder_id}`

👥 **Info Grup:**
• **Nama Grup**: {chat_title}
• **Username Grup**: {chat_username}
• **ID Grup**: `{chat_id}`
• **Jumlah Member**: {member_count}

📅 **Waktu**: {current_time}

━━━━━━━━━━━━━━━━━━
🤖 Bot by denz | @denzwel1
"""

                # Kirim ke saved messages
                await client.send_message('me', notification_msg)
                
                # Log ke console
                logger.info(f"✅ Bot ditambahkan ke grup '{chat_title}' oleh {adder_name} ({adder_id})")
                
                # Kirim pesan sambutan di grup
                try:
                    welcome_msg = f"""
🤖 **Halo semuanya!**

Terima kasih sudah menambahkan saya ke grup **{chat_title}**.

**Fitur yang tersedia:**
• Ganti nama grup (`.u <nama>`)
• Ganti foto grup (`.ppgb`)
• Kirim pesan tersimpan (`.tw`, `.c`, `.lagu`)
• Dan masih banyak lagi!

Ketik `.fitur` untuk melihat semua fitur.

━━━━━━━━━━━━━━━━━━
Bot by denz | @denzwel1
"""
                    await event.reply(welcome_msg)
                except Exception as welcome_error:
                    logger.warning(f"⚠️ Tidak bisa kirim pesan sambutan: {welcome_error}")
                    
    except Exception as e:
        logger.error(f"❌ Error di chat_action_handler: {e}")

# =========================
# FITUR ALTERNATIF: DETEKSI GRUP BARU DARI DIALOG UPDATE
# =========================
@client.on(events.NewMessage)
async def monitor_new_groups(event):
    try:
        # Cek jika ini pesan sistem tentang pembuatan grup
        if event.action:
            action_message = str(event.action)
            if any(keyword in action_message.lower() for keyword in ['create', 'add', 'invite']):
                me = await client.get_me()
                chat = await event.get_chat()
                
                # Cek jika bot ada di daftar participant
                try:
                    participants = await client.get_participants(chat)
                    if me.id in [p.id for p in participants]:
                        # Bot baru ditambahkan ke grup
                        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        
                        notification_msg = f"""
🔔 **BOT DITEMUKAN DI GRUP BARU**

👥 **Info Grup:**
• **Nama Grup**: {getattr(chat, 'title', 'Unknown')}
• **Username**: @{getattr(chat, 'username', 'Tidak ada')}
• **ID Grup**: `{chat.id}`
• **Jumlah Member**: {len(participants)}

📅 **Waktu Deteksi**: {current_time}

💡 **Catatan**: Bot mungkin sudah lama di grup ini, atau baru ditambahkan.

━━━━━━━━━━━━━━━━━━
🤖 Bot by denz | @denzwel1
"""
                        await client.send_message('me', notification_msg)
                        logger.info(f"📝 Bot terdeteksi di grup baru: {getattr(chat, 'title', 'Unknown')}")
                        
                except Exception as part_error:
                    logger.warning(f"⚠️ Tidak bisa cek participants: {part_error}")
                    
    except Exception as e:
        # Skip error untuk avoid spam
        pass

# =========================
# FITUR TEST NOTIFIKASI: .testnotif
# =========================
@client.on(events.NewMessage(pattern=r"\.testnotif$"))
@owner_only
async def test_notification(event):
    """Test notifikasi manual"""
    try:
        chat = await event.get_chat()
        
        test_msg = f"""
🔔 **TEST NOTIFIKASI**

Ini adalah test notifikasi untuk memastikan sistem notifikasi berfungsi.

**Info Grup Saat Ini:**
• **Nama**: {getattr(chat, 'title', 'N/A')}
• **ID**: `{chat.id}`
• **Waktu**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

✅ Jika pesan ini muncul di Saved Messages, berarti sistem notifikasi berfungsi.

━━━━━━━━━━━━━━━━━━
🤖 Bot by denz | @denzwel1
"""
        
        # Kirim test notifikasi ke saved messages
        await client.send_message('me', test_msg)
        await event.reply("✅ Test notifikasi telah dikirim ke Saved Messages. Cek pesan tersimpan Anda!")
        
    except Exception as e:
        await event.reply(f"❌ Error test notifikasi: {e}")

# =========================
# FITUR MANUAL CHECK: .checkgroups (FIXED VERSION)
# =========================
@client.on(events.NewMessage(pattern=r"\.checkgroups$"))
@owner_only
async def manual_check_groups(event):
    """Manual check untuk melihat semua grup"""
    try:
        processing_msg = await event.reply("🔄 Memeriksa semua grup...")
        
        groups = []
        
        async for dialog in client.iter_dialogs():
            if dialog.is_group:
                group_info = {
                    'name': dialog.name,
                    'id': dialog.id,
                    'unread': dialog.unread_count,
                    'archived': dialog.archived
                }
                groups.append(group_info)
        
        # Buat laporan sederhana
        report = f"""
📊 **LAPORAN GRUP MANUAL**

📈 **Statistik:**
• Total Grup: {len(groups)}

📋 **Daftar Grup:**\n"""
        
        for i, group in enumerate(groups[:15], 1):  # Batasi 15 grup pertama
            status = "📁 Archived" if group['archived'] else "✅ Active"
            unread = f"📨 {group['unread']} unread" if group['unread'] > 0 else "📭 No unread"
            report += f"{i}. **{group['name']}**\n"
            report += f"   • ID: `{group['id']}`\n"
            report += f"   • {status} | {unread}\n\n"
        
        if len(groups) > 15:
            report += f"📋 ...dan {len(groups) - 15} grup lainnya\n\n"
        
        report += "━━━━━━━━━━━━━━━━━━\n🤖 Bot by denz | @denzwel1"
        
        await processing_msg.edit(report)
        
    except Exception as e:
        await event.reply(f"❌ Error manual check: {e}")

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

🔔 **Notifikasi**: {'✅ AKTIF' if hasattr(client, '_chat_action_handler') else '❌ TIDAK AKTIF'}
📨 **Broadcast Status**: {'🛑 STOPPED' if stop_share_pm else '✅ READY'}
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
# FITUR: CEK INFO GRUP SEKARANG
# =========================
@client.on(events.NewMessage(pattern=r"\.grpinfo$"))
@owner_only
async def group_info(event):
    try:
        chat = await event.get_chat()
        
        # Dapatkan informasi member
        participants_count = 0
        try:
            async for participant in client.iter_participants(chat):
                participants_count += 1
        except:
            participants_count = "Tidak bisa dihitung"
        
        info_text = f"""
👥 **INFO GRUP SAAT INI**

📝 **Detail Grup:**
• **Nama**: {getattr(chat, 'title', 'N/A')}
• **Username**: @{getattr(chat, 'username', 'N/A')}
• **ID**: `{chat.id}`
• **Tipe**: {'Channel' if getattr(chat, 'broadcast', False) else 'Supergroup' if getattr(chat, 'megagroup', False) else 'Group'}
• **Member**: {participants_count}
• **DC**: {getattr(chat, 'dc_id', 'N/A')}

🔒 **Hak Akses:**
• **Protected**: {getattr(chat, 'restricted', False)}
• **Verified**: {getattr(chat, 'verified', False)}
• **Scam**: {getattr(chat, 'scam', False)}
• **Fake**: {getattr(chat, 'fake', False)}

📊 **Info Lain:**
• **Tanggal Dibuat**: {getattr(chat, 'date', 'N/A')}
• **Restricted Reason**: {getattr(chat, 'restriction_reason', 'Tidak ada')}

━━━━━━━━━━━━━━━━━━
🤖 Bot by denz | @denzwel1
"""
        await event.reply(info_text)
        
    except Exception as e:
        await event.reply(f"❌ Error mendapatkan info grup: {e}")

# =========================
# FITUR: LIST SEMUA GRUP
# =========================
@client.on(events.NewMessage(pattern=r"\.listgrp$"))
@owner_only
async def list_groups(event):
    try:
        processing_msg = await event.reply("🔄 Mengumpulkan daftar grup...")
        
        groups = []
        async for dialog in client.iter_dialogs():
            if dialog.is_group:
                groups.append({
                    'name': dialog.name,
                    'id': dialog.id,
                    'unread': dialog.unread_count,
                    'archived': dialog.archived
                })
        
        if not groups:
            await processing_msg.edit("❌ Bot tidak berada di grup manapun.")
            return
        
        # Buat pesan daftar grup
        list_text = f"👥 **DAFTAR GRUP**\n\n"
        list_text += f"📊 **Total Grup**: {len(groups)}\n\n"
        
        for i, group in enumerate(groups[:20], 1):  # Batasi 20 grup pertama
            status = "📁 Archived" if group['archived'] else "✅ Active"
            unread = f"📨 {group['unread']} unread" if group['unread'] > 0 else "📭 No unread"
            list_text += f"{i}. **{group['name']}**\n"
            list_text += f"   • ID: `{group['id']}`\n"
            list_text += f"   • {status} | {unread}\n\n"
        
        if len(groups) > 20:
            list_text += f"📋 ...dan {len(groups) - 20} grup lainnya\n\n"
        
        list_text += "━━━━━━━━━━━━━━━━━━\n"
        list_text += "🤖 Bot by denz | @denzwel1"
        
        await processing_msg.edit(list_text)
        
    except Exception as e:
        await event.reply(f"❌ Error mendapatkan daftar grup: {e}")

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

**Broadcast Status:**
• **Stop Share PM Flag**: {stop_share_pm}
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
# FITUR: .fitur (UPDATED DENGAN .stopsharepm)
# =========================
@client.on(events.NewMessage(pattern=r"\.fitur$"))
async def fitur_list(event):
    fitur_text = """
🤖 **Daftar Fitur Userbot:**

🎵 **Musik & Download**
• `.song <judul>` — Cari lagu di YouTube
• `.music <judul>` — Cari musik dengan saran
• `.dl <judul>` — Download lagu (alternatif)
• `.get <judul>` — Cari & download lagu
• `.yt <link>` — Download dari YouTube

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

👥 **Manajemen Grup & Broadcast**
• `.u <nama>` — Ubah nama grup langsung
• `.sharegrup` (reply pesan) — Broadcast ke semua grup
• `.sharepm` (reply pesan) — Broadcast ke semua private chat
• `.stopsharepm` — Hentikan broadcast PM yang sedang berjalan
• `.grpinfo` — Info grup saat ini
• `.listgrp` — List semua grup yang diikuti
• `.checkgroups` — Manual check semua grup
• `.checkadmin` — Cek status admin bot

🔔 **Monitoring**
• **Auto-Notif** — Notifikasi otomatis ketika bot ditambahkan ke grup baru
• **Deteksi Otomatis** — Sistem deteksi grup baru
• `.testnotif` — Test notifikasi manual

ℹ️ **Info & Status**
• `.status` — Lihat status server
• `.fitur` — Lihat semua fitur bot
• `.debug` — Info debug untuk troubleshooting
• `.clean` — Bersihkan semua data
• `.info` — Info data tersimpan

🔧 **Utility**
• `.ping` — Test bot response
• `.help` — Bantuan

🔐 **Hanya untuk owner bot**

━━━━━━━━━━━━━━━━━━
🤖 **Bot by denz**
📧 **Contact**: @denzwel1
━━━━━━━━━━━━━━━━━━
"""
    await event.reply(fitur_text)

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
• `.debug` - Debug info
• `.checkadmin` - Check admin status
• `.clean` - Clean all saved data
• `.info` - Show saved data info

🎵 **Music & Download:**
• `.song <judul>` - Search songs on YouTube
• `.music <judul>` - Search music with suggestions
• `.dl <judul>` - Download song (alternatives)
• `.get <judul>` - Search & download options
• `.yt <link>` - Download from YouTube link

👥 **Group Management & Broadcast:**
• `.grpinfo` - Current group info
• `.listgrp` - List all groups
• `.checkgroups` - Manual check all groups
• `.checkadmin` - Check admin rights
• `.sharegrup` - Broadcast to all groups
• `.sharepm` - Broadcast to all private chats
• `.stopsharepm` - Stop ongoing PM broadcast
• `.testnotif` - Test notification system
• **Auto-Notification** - Get notified when bot is added to new groups
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
        logger.info("🔔 Notifikasi sistem AKTIF - Bot akan kirim notifikasi ketika ditambahkan ke grup baru")
        
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

