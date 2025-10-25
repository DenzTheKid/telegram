from telethon import TelegramClient
from telethon.sessions import StringSession
import asyncio

async def main():
    API_ID = 27037133  # Ganti dengan API ID Anda
    API_HASH = "0698732c74d471bca5b7fbba076c52b7"  # Ganti dengan API HASH Anda
    
    client = TelegramClient(StringSession(), API_ID, API_HASH)
    await client.start()
    
    me = await client.get_me()
    print("\n" + "="*60)
    print("✅ SESSION GENERATED SUCCESSFULLY!")
    print("="*60)
    print(f"👤 User: {me.first_name}")
    print(f"📱 Phone: {me.phone}")
    print(f"🆔 ID: {me.id}")
    print("\n🔐 **SESSION STRING:**")
    print("="*60)
    session_string = client.session.save()
    print(session_string)
    print("="*60)
    print("\n💡 **COPY THE STRING ABOVE and set as SESSION_STRING environment variable**")
    
    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
