from telethon import TelegramClient
from telethon.sessions import StringSession
import asyncio

async def main():
    API_ID = int(input("Enter API ID: "))
    API_HASH = input("Enter API HASH: ")
    
    client = TelegramClient(StringSession(), API_ID, API_HASH)
    await client.start()
    
    print("✅ Session created successfully!")
    print("📱 Phone:", (await client.get_me()).phone)
    print(f"🔐 Session String: {client.session.save()}")
    
    await client.disconnect()

asyncio.run(main())
