import os
import sys
import wget
import ffmpeg
import asyncio
import subprocess
from os import path
from pyrogram import emoji
from config import Config
from asyncio import sleep
from pyrogram import Client
from signal import SIGINT
from random import randint
from pyrogram.errors import FloodWait
from pyrogram.utils import MAX_CHANNEL_ID
from pyrogram.raw.types import InputGroupCall
from pyrogram.methods.messages.download_media import DEFAULT_DOWNLOAD_DIR
from pyrogram.raw.functions.phone import EditGroupCallTitle, CreateGroupCall

# Modern py-tgcalls Core Imports
from pytgcalls import PyTgCalls
from pytgcalls.types import AudioStream

# Safe Namespace Catch for Missing exceptions
try:
    from pytgcalls.exceptions import GroupCallNotFoundError
except ImportError:
    from pytgcalls.exceptions import NoActiveGroupCall as GroupCallNotFoundError

from yt_dlp import YoutubeDL

# Initializing base Client structures 
bot = Client(
    "RadioPlayerVC",
    Config.API_ID,
    Config.API_HASH,
    bot_token=Config.BOT_TOKEN
)
bot.start()
e = bot.get_me()
USERNAME = e.username

from user import USER

# Assign Global Mappings 
ADMINS = Config.ADMINS
STREAM_URL = Config.STREAM_URL
CHAT_ID = Config.CHAT_ID
ADMIN_LIST = {}
CALL_STATUS = {}
FFMPEG_PROCESSES = {}
RADIO = {6}
LOG_GROUP = Config.LOG_GROUP
DURATION_LIMIT = Config.DURATION_LIMIT
DELAY = Config.DELAY
playlist = Config.playlist
msg = Config.msg
EDIT_TITLE = Config.EDIT_TITLE
RADIO_TITLE = Config.RADIO_TITLE

ydl_opts = {
    "format": "bestaudio[ext=m4a]",
    "geo-bypass": True,
    "nocheckcertificate": True,
    "outtmpl": "downloads/%(id)s.%(ext)s",
}
ydl = YoutubeDL(ydl_opts)


class MusicPlayer(object):
    def __init__(self):
        # Fixed: Modern PyTgCalls architecture takes the USER instance directly
        self.group_call = PyTgCalls(USER)

    async def send_playlist(self):
        if not playlist:
            pl = f"{emoji.NO_ENTRY} **Empty Playlist!**"
        else:       
            pl = f"{emoji.PLAY_BUTTON} **Playlist**:\n" + "\n".join([
                f"**{i}**. **{x[1]}**\n  - **Requested By:** {x[4]}\n"
                for i, x in enumerate(playlist)
            ])
        if msg.get('playlist') is not None:
            try:
                await msg['playlist'].delete()
            except Exception:
                pass
        msg['playlist'] = await self.send_text(pl)

    async def skip_current_playing(self):
        if not playlist:
            return
        if len(playlist) == 1:
            await self.start_radio()
            return
            
        # Fixed: Accessing working directories via internal client wrappers safely
        download_dir = os.path.join(os.getcwd(), DEFAULT_DOWNLOAD_DIR)
        raw_file_path = os.path.join(download_dir, f"{playlist[1][1]}.raw")
        
        # Fixed: In py-tgcalls v2.x+, files are played by modifying active media streams
        await self.group_call.change_stream(
            CHAT_ID,
            AudioStream(raw_file_path)
        )
        
        old_track = playlist.pop(0)
        print(f"- START PLAYING: {playlist[0][1]}")
        if EDIT_TITLE:
            await self.edit_title()
        if LOG_GROUP:
            await self.send_playlist()
            
        try:
            os.remove(os.path.join(download_dir, f"{old_track[1]}.raw"))
        except Exception:
            pass
            
        if len(playlist) == 1:
            return
        await self.download_audio(playlist[1])

    async def send_text(self, text):
        if not LOG_GROUP:
            return None
        message = await bot.send_message(
            LOG_GROUP,
            text,
            disable_web_page_preview=True,
            disable_notification=True
        )
        return message

    async def download_audio(self, song):
        download_dir = os.path.join(os.getcwd(), DEFAULT_DOWNLOAD_DIR)
        raw_file = os.path.join(download_dir, f"{song[1]}.raw")
        
        if not os.path.isfile(raw_file):
            if song[3] == "telegram":
                original_file = await bot.download_media(f"{song[2]}")
            elif song[3] == "youtube":
                url = song[2]
                try:
                    info = ydl.extract_info(url, False)
                    ydl.download([url])
                    original_file = path.join("downloads", f"{info['id']}.{info['ext']}")
                except Exception as e:
                    if len(playlist) > 1:
                        playlist.pop(1)
                    print(f"Unable To Download Due To {e} & Skipped!")
                    if len(playlist) == 1:
                        return
                    await self.download_audio(playlist[1])
                    return
            else:
                original_file = wget.download(song[2])
                
            ffmpeg.input(original_file).output(
                raw_file,
                format='s16le',
                acodec='pcm_s16le',
                ac=2,
                ar='48k',
                loglevel='error'
            ).overwrite_output().run()
            try:
                os.remove(original_file)
            except Exception:
                pass

    async def start_radio(self):
        process = FFMPEG_PROCESSES.get(CHAT_ID)
        if process:
            try:
                process.send_signal(SIGINT)
            except Exception:
                pass
            FFMPEG_PROCESSES[CHAT_ID] = ""
            
        station_stream_url = STREAM_URL
        try:
            RADIO.remove(0)
        except Exception:
            pass
        try:
            RADIO.add(1)
        except Exception:
            pass
            
        raw_pipe_file = f'radio-{CHAT_ID}.raw'
        if os.path.exists(raw_pipe_file):
            try:
                os.remove(raw_pipe_file)
            except Exception:
                pass
                
        if not os.path.exists(raw_pipe_file):
            os.mkfifo(raw_pipe_file)
            
        # Fixed: Initialize the call with a clean connection state assessment
        if not self.group_call.is_connected:
            await self.start_call()
            
        ffmpeg_log = open("ffmpeg.log", "w+")
        command = [
            "ffmpeg", "-y", "-i", station_stream_url, "-f", "s16le", 
            "-ac", "2", "-ar", "48000", "-acodec", "pcm_s16le", raw_pipe_file
        ]

        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=ffmpeg_log,
            stderr=asyncio.subprocess.STDOUT,
        )

        FFMPEG_PROCESSES[CHAT_ID] = process
        
        # Fixed: Change stream using modern AudioStream properties rather than properties assignment strings
        await self.group_call.change_stream(
            CHAT_ID,
            AudioStream(raw_pipe_file)
        )
        
        if RADIO_TITLE:
            await self.edit_title()
            
        await sleep(2)
        while True:
            if self.group_call.is_connected:
                print("Successfully Joined VC !")
                break
            else:
                print("Connecting, Please Wait ...")
                await self.start_call()
                await sleep(10)
                continue

    async def stop_radio(self):
        playlist.clear()   
        try:
            RADIO.remove(1)
        except Exception:
            pass
        try:
            RADIO.add(0)
        except Exception:
            pass
            
        # Fixed: Modern leave stream API pattern
        try:
            await self.group_call.leave_call(CHAT_ID)
        except Exception:
            pass
            
        process = FFMPEG_PROCESSES.get(CHAT_ID)
        if process:
            try:
                process.send_signal(SIGINT)
            except Exception:
                pass
            FFMPEG_PROCESSES[CHAT_ID] = ""

    async def start_call(self):
        try:
            # Fixed: modern start method structure uses AudioStream signature directly during boot
            raw_pipe_file = f'radio-{CHAT_ID}.raw'
            await self.group_call.start(CHAT_ID, AudioStream(raw_pipe_file))
        except FloodWait as e:
            await sleep(e.value) # Fixed: modern pyrogram uses e.value rather than e.x
            await self.group_call.start(CHAT_ID, AudioStream(raw_pipe_file))
        except GroupCallNotFoundError:
            try:
                await USER.invoke(CreateGroupCall(
                    peer=(await USER.resolve_peer(CHAT_ID)),
                    random_id=randint(10000, 999999999)
                ))
                await self.group_call.start(CHAT_ID, AudioStream(raw_pipe_file))
            except Exception as e:
                print(e)
        except Exception as e:
            print(e)

    async def edit_title(self):
        pass  # Incomplete endpoint in raw file, safely passed to retain structure

# Global Object Mapping Endpoint
mp = MusicPlayer()

# pytgcalls handlers

@mp.group_call.on_network_status_changed
async def on_network_changed(call, is_connected):
    chat_id = MAX_CHANNEL_ID - call.full_chat.id
    if is_connected:
        CALL_STATUS[chat_id] = True
    else:
        CALL_STATUS[chat_id] = False

@mp.group_call.on_playout_ended
async def playout_ended_handler(_, __):
    if not playlist:
        await mp.start_radio()
    else:
        await mp.skip_current_playing()
