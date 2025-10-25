from telethon import TelegramClient
from telethon.sessions import StringSession
import asyncio

async def main():
    API_ID = int(input("Enter API ID: "))
    API_HASH = input("Enter API HASH: ")
    
    client = TelegramClient(StringSession(), API_ID, API_HASH)
    await client.start()
    
    me = await client.get_me()
    print("\n" + "="*50)
    print("✅ SESSION GENERATED SUCCESSFULLY!")
    print("="*50)
    print(f"👤 User: {me.first_name}")
    print(f"📱 Phone: {me.phone}")
    print(f"🆔 ID: {me.id}")
    print("\n🔐 **SESSION STRING:**")
    print("="*50)
    print(client.session.save())
    print("="*50)
    print("\n💡 **COPY THE STRING ABOVE and set as SESSION_STRING environment variable**")
    
    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
