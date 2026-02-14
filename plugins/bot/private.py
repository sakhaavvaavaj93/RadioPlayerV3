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

import asyncio
from config import Config
from utils import USERNAME, mp
from pyrogram import Client, filters, emoji
from pyrogram.errors import MessageNotModified
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

msg=Config.msg
ADMINS=Config.ADMINS
CHAT_ID=Config.CHAT_ID
playlist=Config.playlist
LOG_GROUP=Config.LOG_GROUP

# Constants for duplicated strings
EMPTY_PLAYLIST_MSG = "⛔️ Empty Playlist !"
SEARCH_INLINE_TEXT = "SEARCH SONGS INLINE"
CHANNEL_URL = "https://t.me/AsmSafone"
SUPPORT_URL = "https://t.me/AsmSupport"
MORE_BOTS_TEXT = "MORE BOTS"
MORE_BOTS_URL = "https://t.me/AsmSafone/173"
SOURCE_CODE_TEXT = "SOURCE CODE"
SOURCE_CODE_URL = "https://github.com/AsmSafone/RadioPlayerV3"

# Common button layouts
def get_help_buttons():
    """Returns the help menu button layout."""
    return [
        [
            InlineKeyboardButton(SEARCH_INLINE_TEXT, switch_inline_query_current_chat=""),
        ],
        [
            InlineKeyboardButton("CHANNEL", url=CHANNEL_URL),
            InlineKeyboardButton("SUPPORT", url=SUPPORT_URL),
        ],
        [
            InlineKeyboardButton(MORE_BOTS_TEXT, url=MORE_BOTS_URL),
            InlineKeyboardButton(SOURCE_CODE_TEXT, url=SOURCE_CODE_URL),
        ],
        [
            InlineKeyboardButton("BACK HOME", callback_data="home"),
            InlineKeyboardButton("CLOSE MENU", callback_data="close"),
        ]
    ]


def get_home_buttons():
    """Returns the home menu button layout."""
    return [
        [
            InlineKeyboardButton(SEARCH_INLINE_TEXT, switch_inline_query_current_chat=""),
        ],
        [
            InlineKeyboardButton("CHANNEL", url=CHANNEL_URL),
            InlineKeyboardButton("SUPPORT", url=SUPPORT_URL),
        ],
        [
            InlineKeyboardButton(MORE_BOTS_TEXT, url=MORE_BOTS_URL),
            InlineKeyboardButton(SOURCE_CODE_TEXT, url=SOURCE_CODE_URL),
        ],
        [
            InlineKeyboardButton("❔ HOW TO USE ❔", callback_data="help"),
        ]
    ]


def get_player_buttons():
    """Returns the player control button layout."""
    return [
        [
            InlineKeyboardButton("🔄", callback_data="replay"),
            InlineKeyboardButton("⏸", callback_data="pause"),
            InlineKeyboardButton("⏩", callback_data="skip")
        ],
    ]


def get_player_buttons_paused():
    """Returns the player control button layout when paused."""
    return [
        [
            InlineKeyboardButton("🔄", callback_data="replay"),
            InlineKeyboardButton("▶️", callback_data="resume"),
            InlineKeyboardButton("⏩", callback_data="skip")
        ],
    ]


def format_playlist_text():
    """Helper function to format playlist text."""
    if not playlist:
        return f"{emoji.NO_ENTRY} **Empty Playlist!**"
    else:
        return f"{emoji.PLAY_BUTTON} **Playlist**:\n" + "\n".join([
            f"**{i}**. **{x[1]}**\n  - **Requested By:** {x[4]}"
            for i, x in enumerate(playlist)
        ])


async def handle_replay_callback(query: CallbackQuery):
    """Handle the replay button callback."""
    group_call = mp.group_call
    if not playlist:
        await query.answer(EMPTY_PLAYLIST_MSG, show_alert=True)
        return
    
    group_call.restart_playout()
    pl = format_playlist_text()
    
    try:
        await query.answer("🔂 Replaying !", show_alert=True)
        await query.edit_message_text(
            f"{pl}",
            parse_mode="Markdown",
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(get_player_buttons())
        )
    except MessageNotModified:
        pass


async def handle_pause_callback(query: CallbackQuery):
    """Handle the pause button callback."""
    if not playlist:
        await query.answer(EMPTY_PLAYLIST_MSG, show_alert=True)
        return
    
    mp.group_call.pause_playout()
    pl = format_playlist_text()
    
    try:
        await query.answer("⏸ Paused !", show_alert=True)
        await query.edit_message_text(
            f"{pl}",
            parse_mode="Markdown",
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(get_player_buttons_paused())
        )
    except MessageNotModified:
        pass


async def handle_resume_callback(query: CallbackQuery):
    """Handle the resume button callback."""
    if not playlist:
        await query.answer(EMPTY_PLAYLIST_MSG, show_alert=True)
        return
    
    mp.group_call.resume_playout()
    pl = format_playlist_text()
    
    try:
        await query.answer("▶️ Resumed !", show_alert=True)
        await query.edit_message_text(
            f"{pl}",
            parse_mode="Markdown",
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(get_player_buttons())
        )
    except MessageNotModified:
        pass


async def handle_skip_callback(query: CallbackQuery):
    """Handle the skip button callback."""
    if not playlist:
        await query.answer(EMPTY_PLAYLIST_MSG, show_alert=True)
        return
    
    await mp.skip_current_playing()
    pl = format_playlist_text()
    
    try:
        await query.answer("⏩ Skipped !", show_alert=True)
        await query.edit_message_text(
            f"{pl}",
            parse_mode="Markdown",
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(get_player_buttons())
        )
    except MessageNotModified:
        pass


async def handle_help_callback(query: CallbackQuery):
    """Handle the help button callback."""
    try:
        await query.edit_message_text(
            HELP_TEXT,
            reply_markup=InlineKeyboardMarkup(get_help_buttons())
        )
    except MessageNotModified:
        pass


async def handle_home_callback(query: CallbackQuery):
    """Handle the home button callback."""
    try:
        await query.edit_message_text(
            HOME_TEXT.format(query.from_user.first_name, query.from_user.id),
            reply_markup=InlineKeyboardMarkup(get_home_buttons())
        )
    except MessageNotModified:
        pass


async def handle_close_callback(query: CallbackQuery):
    """Handle the close button callback."""
    try:
        await query.message.delete()
        await query.message.reply_to_message.delete()
    except Exception:
        pass


HOME_TEXT = "👋🏻 **Hi [{}](tg://user?id={})**,\n\nI'm **Radio Player V3.0** \nI Can Play Radio / Music / YouTube Live In Channel & Group 24x7 Nonstop. Made with ❤️ By @AsmSafone 😉!"
HELP_TEXT = """
💡 --**Setting Up**--:

\u2022 Add the bot and user account in your group with admin rights.
\u2022 Start a voice chat in your group & restart the bot if not joined to vc.
\u2022 Use /play [song name] or use /play as a reply to an audio file or youtube link.

💡 --**Common Commands**--:

\u2022 `/help` - shows help for all commands
\u2022 `/song` [song name] - download the song as audio
\u2022 `/current` - shows current track with controls
\u2022 `/playlist` - shows the current & queued playlist

💡 --**Admins Commands**--:

\u2022 `/radio` - start radio stream
\u2022 `/stopradio` - stop radio stream
\u2022 `/skip` - skip current music
\u2022 `/join` - join the voice chat
\u2022 `/leave` - leave the voice chat
\u2022 `/stop` - stop playing music
\u2022 `/volume` - change volume (0-200)
\u2022 `/replay` - play from the beginning
\u2022 `/clean` - remove unused raw files
\u2022 `/pause` - pause playing music
\u2022 `/resume` - resume playing music
\u2022 `/mute` - mute the vc userbot
\u2022 `/unmute` - unmute the vc userbot
\u2022 `/restart` - update & restart the bot
\u2022 `/setvar` - set/change heroku configs

© **Powered By** : 
**@AsmSafone | @AsmSupport** 👑
"""


@Client.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
    if query.from_user.id not in Config.ADMINS and query.data != "help":
        await query.answer("You're Not Allowed! 🤣", show_alert=True)
        return

    query_data = query.data.lower()
    
    if query_data == "replay":
        await handle_replay_callback(query)
    elif query_data == "pause":
        await handle_pause_callback(query)
    elif query_data == "resume":
        await handle_resume_callback(query)
    elif query_data == "skip":
        await handle_skip_callback(query)
    elif query_data == "help":
        await handle_help_callback(query)
    elif query_data == "home":
        await handle_home_callback(query)
    elif query_data == "close":
        await handle_close_callback(query)

    await query.answer()



@Client.on_message(filters.command(["start", f"start@{USERNAME}"]))
async def start(client, message):
    reply_markup = InlineKeyboardMarkup(get_home_buttons())
    m=await message.reply_photo(photo="https://telegra.ph/file/4e839766d45935998e9c6.jpg", caption=HOME_TEXT.format(message.from_user.first_name, message.from_user.id), reply_markup=reply_markup)
    await mp.delete(m)
    await mp.delete(message)


@Client.on_message(filters.command(["help", f"help@{USERNAME}"]))
async def help(client, message):
    reply_markup = InlineKeyboardMarkup(get_help_buttons())
    if msg.get('help') is not None:
        await msg['help'].delete()
    msg['help'] = await message.reply_photo(photo="https://telegra.ph/file/4e839766d45935998e9c6.jpg", caption=HELP_TEXT, reply_markup=reply_markup)
    await mp.delete(message)


@Client.on_message(filters.command(["setvar", f"setvar@{USERNAME}"]) & filters.user(ADMINS) & (filters.chat(CHAT_ID) | filters.private | filters.chat(LOG_GROUP)))
async def set_heroku_var(client, message):
    if not Config.HEROKU_APP:
        buttons = [[InlineKeyboardButton('HEROKU_API_KEY', url='https://dashboard.heroku.com/account/applications/authorizations/new')]]
        k=await message.reply_text(
            text="❗ **No Heroku App Found !** \n__Please Note That, This Command Needs The Following Heroku Vars To Be Set :__ \n\n1. `HEROKU_API_KEY` : Your heroku account api key.\n2. `HEROKU_APP_NAME` : Your heroku app name. \n\n**For More Ask In @AsmSupport !!**", 
            reply_markup=InlineKeyboardMarkup(buttons))
        await mp.delete(k)
        await mp.delete(message)
        return
    if " " in message.text:
        _, env = message.text.split(" ", 1)
        if "=" not in env:
            k=await message.reply_text("❗ **You Should Specify The Value For Variable!** \n\nFor Example: \n`/setvar CHAT_ID=-1001313215676`")
            await mp.delete(k)
            await mp.delete(message)
            return
        var, value = env.split("=", 2)
        config = Config.HEROKU_APP.config()
        if not value:
            m=await message.reply_text(f"❗ **No Value Specified, So Deleting `{var}` Variable !**")
            await asyncio.sleep(2)
            if var in config:
                del config[var]
                await m.edit(f"🗑 **Sucessfully Deleted `{var}` !**")
                config[var] = None
            else:
                await m.edit(f"🤷‍♂️ **Variable Named `{var}` Not Found, Nothing Was Changed !**")
            return
        if var in config:
            m=await message.reply_text(f"⚠️ **Variable Already Found, So Edited Value To `{value}` !**")
        else:
            m=await message.reply_text("⚠️ **Variable Not Found, So Setting As New Var !**")
        await asyncio.sleep(2)
        await m.edit(f"✅ **Succesfully Set Variable `{var}` With Value `{value}`, Now Restarting To Apply Changes !**")
        config[var] = str(value)
        await mp.delete(m)
        await mp.delete(message)
    else:
        k=await message.reply_text("❗ **You Haven't Provided Any Variable, You Should Follow The Correct Format !** \n\nFor Example: \n• `/setvar CHAT_ID=-1001313215676` to change or set CHAT var. \n• `/setvar REPLY_MESSAGE=` to delete REPLY_MESSAGE var.")
        await mp.delete(k)
        await mp.delete(message)
