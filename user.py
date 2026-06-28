
from config import Config
from pyrogram import Client

REPLY_MESSAGE = Config.REPLY_MESSAGE

if REPLY_MESSAGE is not None:
    USER = Client(
        name=Config.SESSION if Config.SESSION else "RadioUserSession", # Fixed: Explicit keyword argument
        api_id=Config.API_ID,
        api_hash=Config.API_HASH,
        plugins=dict(root="plugins.userbot")
    )
else:
    USER = Client(
        name=Config.SESSION if Config.SESSION else "RadioUserSession", # Fixed: Explicit keyword argument
        api_id=Config.API_ID,
        api_hash=Config.API_HASH
    )

# Fixed: Removed USER.start() from here to let main.py manage it inside the async event loop safely.
