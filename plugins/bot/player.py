"""
RadioPlayerV3, Telegram Voice Chat Bot
Copyright (c) 2021  Asm Safone <https://github.com/AsmSafone>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>
"""

import os
import re
import ffmpeg
import asyncio
import subprocess
from config import Config
from signal import SIGINT
from yt_dlp import YoutubeDL
from youtube_search import YoutubeSearch
from pyrogram import Client, filters, emoji
from utils import mp, RADIO, USERNAME, FFMPEG_PROCESSES
from pyrogram.methods.messages.download_media import DEFAULT_DOWNLOAD_DIR
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton


msg=Config.msg
playlist=Config.playlist
ADMINS=Config.ADMINS
CHAT_ID=Config.CHAT_ID
LOG_GROUP=Config.LOG_GROUP
RADIO_TITLE=Config.RADIO_TITLE
EDIT_TITLE=Config.EDIT_TITLE
ADMIN_ONLY=Config.ADMIN_ONLY
DURATION_LIMIT=Config.DURATION_LIMIT

async def is_admin(_, client, message: Message):
    admins = await mp.get_admins(CHAT_ID)
    if message.from_user is None and message.sender_chat:
        return True
    if message.from_user and message.from_user.id in admins:
        return True
    else:
        return False

ADMINS_FILTER = filters.create(is_admin)


def stop_radio_if_playing(group_call):
    """Helper function to stop radio if currently playing."""
    if 1 in RADIO:
        if group_call:
            group_call.input_filename = ''
            RADIO.remove(1)
            RADIO.add(0)
        process = FFMPEG_PROCESSES.get(CHAT_ID)
        if process:
            try:
                process.send_signal(SIGINT)
            except subprocess.TimeoutExpired:
                process.kill()
            except Exception as e:
                print(e)
            FFMPEG_PROCESSES[CHAT_ID] = ""


async def start_playing_audio(group_call, client_workdir, file_id):
    """Helper function to start playing audio file."""
    if not group_call.is_connected:
        await mp.start_call()
    group_call.input_filename = os.path.join(
        client_workdir,
        DEFAULT_DOWNLOAD_DIR,
        f"{file_id}.raw"
    )
    print(f"- START PLAYING: {file_id}")


def format_playlist():
    """Helper function to format playlist display."""
    if not playlist:
        return f"{emoji.NO_ENTRY} **Empty Playlist!**"
    else:
        return f"{emoji.PLAY_BUTTON} **Playlist**:\n" + "\n".join([
            f"**{i}**. **{x[1]}**\n  - **Requested By:** {x[4]}"
            for i, x in enumerate(playlist)
        ])


async def send_playlist_message(message, pl):
    """Helper function to send playlist to appropriate chat."""
    if EDIT_TITLE:
        await mp.edit_title()
    if message.chat.type == "private":
        await message.reply_text(pl)
    elif LOG_GROUP:
        await mp.send_playlist()
    elif not LOG_GROUP and message.chat.type == "supergroup":
        k = await message.reply_text(pl)
        await mp.delete(k)


async def handle_audio_playback(message, m_audio, user):
    """Helper function to handle audio file playback."""
    if round(m_audio.audio.duration / 60) > DURATION_LIMIT:
        d = await message.reply_text(
            f"❌ __Audios Longer Than {DURATION_LIMIT} Minute(s) Aren't Allowed, "
            f"The Provided Audio Is {round(m_audio.audio.duration/60)} Minute(s)!__"
        )
        await mp.delete(d)
        await mp.delete(message)
        return False
    
    data = {1: m_audio.audio.title, 2: m_audio.audio.file_id, 3: "telegram", 4: user}
    playlist.append(data)
    
    if len(playlist) == 1:
        group_call = mp.group_call
        m_status = await message.reply_text("⚡️")
        await mp.download_audio(playlist[0])
        stop_radio_if_playing(group_call)
        await start_playing_audio(group_call, message._client.workdir, playlist[0][1])
        await m_status.delete()
    
    pl = format_playlist()
    await send_playlist_message(message, pl)
    
    for track in playlist[:2]:
        await mp.download_audio(track)
    
    return True


def get_youtube_info(url):
    """Helper function to extract YouTube video information."""
    ydl_opts = {
        "geo-bypass": True,
        "nocheckcertificate": True
    }
    ydl = YoutubeDL(ydl_opts)
    try:
        info = ydl.extract_info(url, False)
        return info
    except Exception as e:
        print(e)
        raise


async def handle_youtube_playback(message, url, user, msg):
    """Helper function to handle YouTube video playback."""
    try:
        info = get_youtube_info(url)
    except Exception as e:
        k = await msg.edit(f"❌ **YouTube Download Error !** \n\n{e}")
        print(str(e))
        await mp.delete(message)
        await mp.delete(k)
        return False
    
    duration = round(info["duration"] / 60)
    title = info["title"]
    
    if int(duration) > DURATION_LIMIT:
        k = await message.reply_text(
            f"❌ __Videos Longer Than {DURATION_LIMIT} Minute(s) Aren't Allowed, "
            f"The Provided Video Is {duration} Minute(s)!__"
        )
        await mp.delete(k)
        await mp.delete(message)
        return False
    
    data = {1: title, 2: url, 3: "youtube", 4: user}
    playlist.append(data)
    
    group_call = mp.group_call
    client = group_call.client
    
    if len(playlist) == 1:
        m_status = await msg.edit("⚡️")
        await mp.download_audio(playlist[0])
        stop_radio_if_playing(group_call)
        await start_playing_audio(group_call, client.workdir, playlist[0][1])
        await m_status.delete()
    else:
        await msg.delete()
    
    pl = format_playlist()
    await send_playlist_message(message, pl)
    
    for track in playlist[:2]:
        await mp.download_audio(track)
    
    return True


@Client.on_message(filters.command(["play", f"play@{USERNAME}"]) & (filters.chat(CHAT_ID) | filters.private | filters.chat(LOG_GROUP)) | filters.audio & filters.private)
async def yplay(_, message: Message):
    if ADMIN_ONLY == "True":
        admins = await mp.get_admins(CHAT_ID)
        if message.from_user.id not in admins:
            m = await message.reply_sticker("CAACAgUAAxkBAAEBpyZhF4R-ZbS5HUrOxI_MSQ10hQt65QACcAMAApOsoVSPUT5eqj5H0h4E")
            await mp.delete(m)
            await mp.delete(message)
            return
    
    # Parse media type from message
    media_type, yturl, ysearch, m_audio = parse_media_type(message)
    
    # Validate input
    if not media_type:
        d = await message.reply_text("❗️ __You Didn't Give Me Anything To Play, Send Me An Audio File or Reply /play To An Audio File!__")
        await mp.delete(d)
        await mp.delete(message)
        return
    
    user = f"[{message.from_user.first_name}](tg://user?id={message.from_user.id})"
    
    # Handle audio playback
    if media_type == "audio":
        await handle_audio_playback(message, m_audio, user)
        await mp.delete(message)
        return
    
    # Handle YouTube or search query playback
    if media_type == "youtube":
        msg = await message.reply_text("🔍")
        url = yturl
    elif media_type == "query":
        url, msg = await handle_youtube_search(ysearch, message)
        if url is None:
            return
    else:
        return
    
    await handle_youtube_playback(message, url, user, msg)
    await mp.delete(message)


@Client.on_message(filters.command(["current", f"current@{USERNAME}"]) & (filters.chat(CHAT_ID) | filters.private | filters.chat(LOG_GROUP)))
async def current(_, m: Message):
    if not playlist:
        k=await m.reply_text(f"{emoji.NO_ENTRY} **Nothing Is Playing!**")
        await mp.delete(k)
        await m.delete()
        return
    else:
        pl = f"{emoji.PLAY_BUTTON} **Playlist**:\n" + "\n".join([
            f"**{i}**. **{x[1]}**\n  - **Requested By:** {x[4]}"
            for i, x in enumerate(playlist)
            ])
    if m.chat.type == "private":
        await m.reply_text(
            pl,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("🔄", callback_data="replay"),
                        InlineKeyboardButton("⏸", callback_data="pause"),
                        InlineKeyboardButton("⏭", callback_data="skip")
                    
                    ],

                ]
                )
        )
    else:
        if msg.get('playlist') is not None:
            await msg['playlist'].delete()
        msg['playlist'] = await m.reply_text(
            pl,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("🔄", callback_data="replay"),
                        InlineKeyboardButton("⏸", callback_data="pause"),
                        InlineKeyboardButton("⏭", callback_data="skip")
                    
                    ],

                ]
                )
        )
    await mp.delete(m)


@Client.on_message(filters.command(["volume", f"volume@{USERNAME}"]) & ADMINS_FILTER & (filters.chat(CHAT_ID) | filters.private | filters.chat(LOG_GROUP)))
async def set_vol(_, m: Message):
    group_call = mp.group_call
    if not group_call.is_connected:
        k=await m.reply_text(f"{emoji.ROBOT} **Didn't Joined Any Voice Chat!**")
        await mp.delete(k)
        await mp.delete(m)
        return
    if len(m.command) < 2:
        k=await m.reply_text(f"{emoji.ROBOT} **You Forgot To Pass Volume (0-200)!**")
        await mp.delete(k)
        await mp.delete(m)
        return
    await group_call.set_my_volume(int(m.command[1]))
    k=await m.reply_text(f"{emoji.SPEAKER_MEDIUM_VOLUME} **Volume Set To {m.command[1]}!**")
    await mp.delete(k)
    await mp.delete(m)


async def send_playlist_to_chat(m: Message, pl: str):
    """Helper function to send playlist based on chat type."""
    if m.chat.type == "private":
        await m.reply_text(pl)
    if LOG_GROUP:
        await mp.send_playlist()
    elif not LOG_GROUP and m.chat.type == "supergroup":
        k = await m.reply_text(pl)
        await mp.delete(k)


async def skip_single_track(m: Message):
    """Helper function to skip the current playing track."""
    await mp.skip_current_playing()
    pl = format_playlist()
    await send_playlist_to_chat(m, pl)


async def skip_multiple_tracks(m: Message, items: list):
    """Helper function to skip multiple tracks from playlist."""
    text = []
    for i in items:
        if 2 <= i <= (len(playlist) - 1):
            audio = f"{playlist[i][1]}"
            playlist.pop(i)
            text.append(f"{emoji.WASTEBASKET} **Succesfully Skipped** - {i}. **{audio}**")
        else:
            text.append(f"{emoji.CROSS_MARK} **Can't Skip First Two Song** - {i}")
    
    k = await m.reply_text("\n".join(text))
    await mp.delete(k)
    
    pl = format_playlist()
    await send_playlist_to_chat(m, pl)


def parse_media_type(message: Message):
    """Helper function to parse and determine media type from message."""
    media_type = ""
    yturl = ""
    ysearch = ""
    m_audio = None
    
    if message.audio:
        media_type = "audio"
        m_audio = message
    elif message.reply_to_message and message.reply_to_message.audio:
        media_type = "audio"
        m_audio = message.reply_to_message
    else:
        youtube_regex = r"^(https?\:\/\/)?(www\.youtube\.com|youtu\.?be)\/.+"
        
        if message.reply_to_message:
            link = message.reply_to_message.text
            if re.match(youtube_regex, link):
                media_type = "youtube"
                yturl = link
        elif " " in message.text:
            text = message.text.split(" ", 1)
            query = text[1]
            if re.match(youtube_regex, query):
                media_type = "youtube"
                yturl = query
            else:
                media_type = "query"
                ysearch = query
    
    return media_type, yturl, ysearch, m_audio


async def handle_youtube_search(ysearch: str, message: Message):
    """Helper function to search YouTube and return URL."""
    try:
        msg = await message.reply_text("🔍")
        results = YoutubeSearch(ysearch, max_results=1).to_dict()
        url = f"https://youtube.com{results[0]['url_suffix']}"
        return url, msg
    except Exception as e:
        msg = await message.reply_text("🔍")
        await msg.edit("**Literary Found Noting!\nTry Searching On Inline 😉!**")
        print(str(e))
        await mp.delete(msg)
        await mp.delete(message)
        return None, None


@Client.on_message(filters.command(["skip", f"skip@{USERNAME}"]) & ADMINS_FILTER & (filters.chat(CHAT_ID) | filters.private | filters.chat(LOG_GROUP)))
async def skip_track(_, m: Message):
    group_call = mp.group_call
    if not group_call.is_connected:
        k = await m.reply_text(f"{emoji.NO_ENTRY} **Nothing Is Playing To Skip!**")
        await mp.delete(k)
        await m.delete()
        return
    
    if len(m.command) == 1:
        await skip_single_track(m)
    else:
        try:
            items = list(dict.fromkeys(m.command[1:]))
            items = [int(x) for x in items if x.isdigit()]
            items.sort(reverse=True)
            await skip_multiple_tracks(m, items)
        except (ValueError, TypeError):
            k = await m.reply_text(f"{emoji.NO_ENTRY} **Invalid Input!**", disable_web_page_preview=True)
            await mp.delete(k)
    
    await mp.delete(m)


@Client.on_message(filters.command(["join", f"join@{USERNAME}"]) & ADMINS_FILTER & (filters.chat(CHAT_ID) | filters.private | filters.chat(LOG_GROUP)))
async def join_group_call(client, m: Message):
    group_call = mp.group_call
    if group_call.is_connected:
        k=await m.reply_text(f"{emoji.ROBOT} **Already Joined To The Voice Chat!**")
        await mp.delete(k)
        await mp.delete(m)
        return
    await mp.start_call()
    chat = await client.get_chat(CHAT_ID)
    k=await m.reply_text(f"{emoji.CHECK_MARK_BUTTON} **Joined The Voice Chat In {chat.title} Successfully!**")
    await mp.delete(k)
    await mp.delete(m)


@Client.on_message(filters.command(["leave", f"leave@{USERNAME}"]) & ADMINS_FILTER & (filters.chat(CHAT_ID) | filters.private | filters.chat(LOG_GROUP)))
async def leave_voice_chat(_, m: Message):
    group_call = mp.group_call
    if not group_call.is_connected:
        k=await m.reply_text(f"{emoji.ROBOT} **Didn't Joined Any Voice Chat!**")
        await mp.delete(k)
        await mp.delete(m)
        return
    playlist.clear()
    if 1 in RADIO:
        await mp.stop_radio()
    group_call.input_filename = ''
    await group_call.stop()
    k=await m.reply_text(f"{emoji.CROSS_MARK_BUTTON} **Left From The Voice Chat Successfully!**")
    await mp.delete(k)
    await mp.delete(m)



@Client.on_message(filters.command(["stop", f"stop@{USERNAME}"]) & ADMINS_FILTER & (filters.chat(CHAT_ID) | filters.private | filters.chat(LOG_GROUP)))
async def stop_playing(_, m: Message):
    group_call = mp.group_call
    if not group_call.is_connected:
        k=await m.reply_text(f"{emoji.NO_ENTRY} **Nothing Is Playing To Stop!**")
        await mp.delete(k)
        await mp.delete(m)
        return
    if 1 in RADIO:
        await mp.stop_radio()
    group_call.stop_playout()
    k=await m.reply_text(f"{emoji.STOP_BUTTON} **Stopped Playing!**")
    playlist.clear()
    await mp.delete(k)
    await mp.delete(m)


@Client.on_message(filters.command(["replay", f"replay@{USERNAME}"]) & ADMINS_FILTER & (filters.chat(CHAT_ID) | filters.private | filters.chat(LOG_GROUP)))
async def restart_playing(_, m: Message):
    group_call = mp.group_call
    if not group_call.is_connected:
        k=await m.reply_text(f"{emoji.NO_ENTRY} **Nothing Is Playing To Replay!**")
        await mp.delete(k)
        await mp.delete(m)
        return
    if not playlist:
        k=await m.reply_text(f"{emoji.NO_ENTRY} **Empty Playlist!**")
        await mp.delete(k)
        await mp.delete(m)
        return
    group_call.restart_playout()
    k=await m.reply_text(
        f"{emoji.COUNTERCLOCKWISE_ARROWS_BUTTON}  "
        "**Playing From The Beginning!**"
    )
    await mp.delete(k)
    await mp.delete(m)


@Client.on_message(filters.command(["pause", f"pause@{USERNAME}"]) & ADMINS_FILTER & (filters.chat(CHAT_ID) | filters.private | filters.chat(LOG_GROUP)))
async def pause_playing(_, m: Message):
    group_call = mp.group_call
    if not group_call.is_connected:
        k=await m.reply_text(f"{emoji.NO_ENTRY} **Nothing Is Playing To Pause!**")
        await mp.delete(k)
        await mp.delete(m)
        return
    mp.group_call.pause_playout()
    k=await m.reply_text(f"{emoji.PLAY_OR_PAUSE_BUTTON} **Paused Playing!**",
                               quote=False)
    await mp.delete(k)
    await mp.delete(m)



@Client.on_message(filters.command(["resume", f"resume@{USERNAME}"]) & ADMINS_FILTER & (filters.chat(CHAT_ID) | filters.private | filters.chat(LOG_GROUP)))
async def resume_playing(_, m: Message):
    if not mp.group_call.is_connected:
        k=await m.reply_text(f"{emoji.NO_ENTRY} **Nothing Is Paused To Resume!**")
        await mp.delete(k)
        await mp.delete(m)
        return
    mp.group_call.resume_playout()
    k=await m.reply_text(f"{emoji.PLAY_OR_PAUSE_BUTTON} **Resumed Playing!**",
                               quote=False)
    await mp.delete(k)
    await mp.delete(m)

@Client.on_message(filters.command(["clean", f"clean@{USERNAME}"]) & ADMINS_FILTER & (filters.chat(CHAT_ID) | filters.private | filters.chat(LOG_GROUP)))
async def clean_raw_pcm(client, m: Message):
    download_dir = os.path.join(client.workdir, DEFAULT_DOWNLOAD_DIR)
    all_fn: list[str] = os.listdir(download_dir)
    for track in playlist[:2]:
        track_fn = f"{track[1]}.raw"
        if track_fn in all_fn:
            all_fn.remove(track_fn)
    count = 0
    if all_fn:
        for fn in all_fn:
            if fn.endswith(".raw"):
                count += 1
                os.remove(os.path.join(download_dir, fn))
    k=await m.reply_text(f"{emoji.WASTEBASKET} **Cleaned {count} Files!**")
    await mp.delete(k)
    await mp.delete(m)


@Client.on_message(filters.command(["mute", f"mute@{USERNAME}"]) & ADMINS_FILTER & (filters.chat(CHAT_ID) | filters.private | filters.chat(LOG_GROUP)))
async def mute(_, m: Message):
    group_call = mp.group_call
    if not group_call.is_connected:
        k=await m.reply_text(f"{emoji.NO_ENTRY} **Nothing Is Playing To Mute!**")
        await mp.delete(k)
        await mp.delete(m)
        return
    await group_call.set_is_mute(True)
    k=await m.reply_text(f"{emoji.MUTED_SPEAKER} **User Muted!**")
    await mp.delete(k)
    await mp.delete(m)

@Client.on_message(filters.command(["unmute", f"unmute@{USERNAME}"]) & ADMINS_FILTER & (filters.chat(CHAT_ID) | filters.private | filters.chat(LOG_GROUP)))
async def unmute(_, m: Message):
    group_call = mp.group_call
    if not group_call.is_connected:
        k=await m.reply_text(f"{emoji.NO_ENTRY} **Nothing Is Muted To Unmute!**")
        await mp.delete(k)
        await mp.delete(m)
        return
    await group_call.set_is_mute(False)
    k=await m.reply_text(f"{emoji.SPEAKER_MEDIUM_VOLUME} **User Unmuted!**")
    await mp.delete(k)
    await mp.delete(m)

@Client.on_message(filters.command(["playlist", f"playlist@{USERNAME}"]) & (filters.chat(CHAT_ID) | filters.private | filters.chat(LOG_GROUP)))
async def show_playlist(_, m: Message):
    if not playlist:
        k=await m.reply_text(f"{emoji.NO_ENTRY} **Nothing Is Playing!**")
        await mp.delete(k)
        await mp.delete(m)
        return
    else:
        pl = f"{emoji.PLAY_BUTTON} **Playlist**:\n" + "\n".join([
            f"**{i}**. **{x[1]}**\n  - **Requested By:** {x[4]}"
            for i, x in enumerate(playlist)
            ])
    if m.chat.type == "private":
        await m.reply_text(pl)
    else:
        if msg.get('playlist') is not None:
            await msg['playlist'].delete()
        msg['playlist'] = await m.reply_text(pl)
    await mp.delete(m)

admincmds=["join", "unmute", "mute", "leave", "clean", "pause", "resume", "stop", "skip", "radio", "stopradio", "replay", "restart", "volume", f"volume@{USERNAME}", f"join@{USERNAME}", f"unmute@{USERNAME}", f"mute@{USERNAME}", f"leave@{USERNAME}", f"clean@{USERNAME}", f"pause@{USERNAME}", f"resume@{USERNAME}", f"stop@{USERNAME}", f"skip@{USERNAME}", f"radio@{USERNAME}", f"stopradio@{USERNAME}", f"replay@{USERNAME}", f"restart@{USERNAME}"]

@Client.on_message(filters.command(admincmds) & ~ADMINS_FILTER & (filters.chat(CHAT_ID) | filters.private | filters.chat(LOG_GROUP)))
async def notforu(_, m: Message):
    k=await m.reply_sticker("CAACAgUAAxkBAAEBpyZhF4R-ZbS5HUrOxI_MSQ10hQt65QACcAMAApOsoVSPUT5eqj5H0h4E")
    await mp.delete(k)
    await mp.delete(m)

allcmd = ["play", "current", "playlist", "song", f"song@{USERNAME}", f"play@{USERNAME}", f"current@{USERNAME}", f"playlist@{USERNAME}"] + admincmds

@Client.on_message(filters.command(allcmd) & filters.group & ~filters.chat(CHAT_ID) & ~filters.chat(LOG_GROUP))
async def not_chat(_, m: Message):
    buttons = [
            [
                InlineKeyboardButton("CHANNEL", url="https://t.me/AsmSafone"),
                InlineKeyboardButton("SUPPORT", url="https://t.me/AsmSupport"),
            ],
            [
                InlineKeyboardButton("🤖 MAKE YOUR OWN BOT 🤖", url="https://heroku.com/deploy?template=https://github.com/AsmSafone/RadioPlayerV3"),
            ]
         ]
    await m.reply_photo(photo="https://telegra.ph/file/4e839766d45935998e9c6.jpg", caption="**Sorry, You Can't Use This Bot In This Group! 🤷‍♂️ But You Can Make Your Own Bot Like This From The [Source Code](https://github.com/AsmSafone/RadioPlayerV3) Below 😉!**", reply_markup=InlineKeyboardMarkup(buttons))
    await mp.delete(m)
