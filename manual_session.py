from telethon.sync import TelegramClient
from telethon.sessions import StringSession

API_ID = 27037133
API_HASH = "0698732c74d471bca5b7fbba076c52b7"

client = TelegramClient(StringSession(), API_ID, API_HASH)
client.start(phone="YOUR_PHONE_NUMBER")
session_string = client.session.save()
print("SESSION:", session_string)
