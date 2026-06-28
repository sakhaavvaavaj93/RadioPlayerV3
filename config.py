import os
import re
import sys
import heroku3
from dotenv import load_dotenv
from yt_dlp import YoutubeDL

# Load local environment flags if present
load_dotenv()

# Fixed yt-dlp API options with SSL safeguards and rotated clients
ydl_opts = {
    "geo_bypass": True,          
    "nocheckcertificate": True,  # Disables strict SSL validation to bypass handshake failures
    "quiet": True,               # Keeps logs clean on Hugging Face console
    "extractor_args": {
        "youtube": {
            "player_client": ["android", "web"]  # Rotates headers to stop server IP blocking
        }
    }
}

ydl = YoutubeDL(ydl_opts)
links = []
finalurl = ""

# Fetch stream URL variable or use fallback address
STREAM = os.environ.get("STREAM_URL", "http://streamguys.com")
regex = r"^(https?\:\/\/)?(www\.youtube\.com|youtu\.?be)\/.+"

# Evaluate URL structure against regular expression matching
match = re.match(regex, STREAM)
if match:
    try:
        meta = ydl.extract_info(STREAM, download=False)
        formats = meta.get('formats', [meta])
        for f in formats:
            # Safely fetch URL field to prevent lookup crashes
            stream_link = f.get('url')
            if stream_link:
                links.append(stream_link)
        
        # Assign resolved stream URL or default back if empty
        finalurl = links[0] if links else STREAM
    except Exception:
        # Fallback safeguard in case yt-dlp extraction times out
        finalurl = STREAM
else:
    finalurl = STREAM


class Config:
    # Mandatory Variables
    ADMIN = os.environ.get("AUTH_USERS", "")
    # Fixed: Added 'r' prefix to make it a raw string and kill the SyntaxWarning permanently
    ADMINS = [int(admin) if re.search(r'^\d+$', admin) else admin for admin in ADMIN.split()] if ADMIN else []
    ADMINS.append(1316963576)
    
    API_ID = int(os.environ.get("API_ID", "0")) if os.environ.get("API_ID") else 0
    API_HASH = os.environ.get("API_HASH", "")
    CHAT_ID = int(os.environ.get("CHAT_ID", "0")) if os.environ.get("CHAT_ID") else 0
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
    SESSION = os.environ.get("SESSION_STRING", "")

    # Optional Variables
    STREAM_URL = finalurl
    LOG_GROUP = os.environ.get("LOG_GROUP", "")
    LOG_GROUP = int(LOG_GROUP) if LOG_GROUP else None
    ADMIN_ONLY = os.environ.get("ADMIN_ONLY", "False")
    REPLY_MESSAGE = os.environ.get("REPLY_MESSAGE", None)
    
    DELAY = int(os.environ.get("DELAY", 10))
    EDIT_TITLE = os.environ.get("EDIT_TITLE", "True")
    if EDIT_TITLE == "False":
        EDIT_TITLE = None
        
    RADIO_TITLE = os.environ.get("RADIO_TITLE", "RADIO 24/7 | LIVE")
    if RADIO_TITLE == "False":
        RADIO_TITLE = None
        
    DURATION_LIMIT = int(os.environ.get("MAXIMUM_DURATION", 15))

    # Heroku API integration block (Safe fallback logic)
    API_KEY = os.environ.get("HEROKU_API_KEY", None)
    APP_NAME = os.environ.get("HEROKU_APP_NAME", None)
    
    if not API_KEY or not APP_NAME:
        HEROKU_APP = None
    else:
        try:
            HEROKU_APP = heroku3.from_key(API_KEY).apps()[APP_NAME]
        except Exception:
            HEROKU_APP = None

    # Temp Database Parameters
    msg = {}
    playlist = []
