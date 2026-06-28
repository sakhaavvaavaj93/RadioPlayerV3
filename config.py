import os
import re
import sys
import heroku3
from dotenv import load_dotenv
from yt_dlp import YoutubeDL
ydl_opts = {
    "geo_bypass": True,          
    "nocheckcertificate": True,  
    "quiet": True,               
    "proxy": os.environ.get("PROXY_URL", None), # Added: Uses a proxy if added to Space Settings
    "extractor_args": {
        "youtube": {
            "player_client": ["android", "web"]  
        }
    }
}
# Load local environment flags if present
load_dotenv()
# Fixed yt-dlp API options with advanced bypass parameters
ydl_opts = {
    "geo_bypass": True,          
    "nocheckcertificate": True,  # Bypasses strict handshake exceptions
    "quiet": True,               
    "extractor_args": {
        "youtube": {
            "player_client": ["android", "web"]  # Bypasses cloud platform blocking filters
        }
    }
}
# Fetch stream URL variable or use fallback address
STREAM = os.environ.get("STREAM_URL", "http://streamguys.com")
def get_live_stream_url(url_source):
    """
    Safely resolves stream URLs synchronously during class configuration loading.
    If yt-dlp triggers an SSL error on Hugging Face, it will immediately fall back 
    to the source URL without breaking the bot's booting cycle.
    """
    regex = r"^(https?\:\/\/)?(www\.youtube\.com|youtu\.?be)\/.+"
    if not re.match(regex, url_source):
        return url_source

    try:
        # Wrap instantiation and extraction locally to contain errors
        with YoutubeDL(ydl_opts) as ydl:
            meta = ydl.extract_info(url_source, download=False)
            formats = meta.get('formats', [meta])
            links = [f.get('url') for f in formats if f.get('url')]
            return links[0] if links else url_source
    except Exception as e:
        print(f"[Warning] yt-dlp extraction failed due to cloud restrictions: {e}")
        return url_source

# Dynamic variable resolution mapping
finalurl = get_live_stream_url(STREAM)
class Config:
    # Mandatory Variables
    ADMIN = os.environ.get("AUTH_USERS", "")
    # Raw String definition prevents SyntaxWarning
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
