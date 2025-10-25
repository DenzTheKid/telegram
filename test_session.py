import os
import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession

async def test_session():
    SESSION_STRING = "1BVtsOKEBu3XwLhJPS_Mo2LPtHmL1RSXgxm1k-Q1y1xEw2KYJWdtzuFY5O2QWZUhbrkDreDyCvR8AVgi4QPhrHbw10i4FPJV6O5rHTkDihT2ZvxM2v_XGhi8Y7sF5_oII2ES2KqHKqnZopSukXuQ5-VC4ckAqkQ-HZtBhYERwQ9NP9f7ycKN6pot1on2AHUxbO5sTB-PlqmrUKGUQvg1J6E5NCeMRO4AApMGP-IxWnn1bG0PFGoFF3xd2gFZpwP-Pab0yXbA6mgzQZ_jQzaVaV0ahl82UmzbSbPvExQix_3Jnl9jMocz3F9IncZ9VmR7PjxPaDk9ozNfgZe-Q5WuAnDop0N1tw60="
    API_ID = 27037133
    API_HASH = "0698732c74d471bca5b7fbba076c52b7"
    
    print("🔐 Testing session string...")
    
    try:
        async with TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH) as client:
            # Test connection
            me = await client.get_me()
            print(f"✅ Session valid! Connected as: {me.first_name} (ID: {me.id})")
            return True
    except Exception as e:
        print(f"❌ Session invalid: {e}")
        return False

if __name__ == '__main__':
    asyncio.run(test_session())
