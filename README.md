# 📻 Telegram Radio Player V3

[![Mentioned in Awesome Telegram Calls](https://awesome.re/mentioned-badge-flat.svg)](https://github.com/tgcalls/awesome-tgcalls)
[![Stars](https://img.shields.io/github/stars/AsmSafone/RadioPlayerV3?style=flat\&color=blue)](https://github.com/AsmSafone/RadioPlayerV3/stargazers)
[![Forks](https://img.shields.io/github/forks/AsmSafone/RadioPlayerV3?style=flat\&color=green)](https://github.com/AsmSafone/RadioPlayerV3/network/members)
[![Issues](https://img.shields.io/github/issues/AsmSafone/RadioPlayerV3)](https://github.com/AsmSafone/RadioPlayerV3/issues)
[![Closed Issues](https://img.shields.io/github/issues-closed/AsmSafone/RadioPlayerV3)](https://github.com/AsmSafone/RadioPlayerV3/issues?q=is%3Aissue+is%3Aclosed)
[![Pull Requests](https://img.shields.io/github/issues-pr/AsmSafone/RadioPlayerV3)](https://github.com/AsmSafone/RadioPlayerV3/pulls)
[![Contributors](https://img.shields.io/github/contributors/AsmSafone/RadioPlayerV3?style=flat)](https://github.com/AsmSafone/RadioPlayerV3/graphs/contributors)
[![Repo Size](https://img.shields.io/github/repo-size/AsmSafone/RadioPlayerV3?color=red)](https://github.com/AsmSafone/RadioPlayerV3)
[![Commit Activity](https://img.shields.io/github/commit-activity/m/AsmSafone/RadioPlayerV3)](https://github.com/AsmSafone/RadioPlayerV3/commits/main)
[![License](https://img.shields.io/github/license/AsmSafone/RadioPlayerV3)](LICENSE)
[![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=LightYagami28_RadioPlayerV3\&metric=security_rating)](https://sonarcloud.io/summary/new_code?id=LightYagami28_RadioPlayerV3)
[![Updates](https://img.shields.io/badge/Updates-Telegram%20Channel-green)](https://t.me/AsmSafone)
[![Support](https://img.shields.io/badge/Support-Group-blue)](https://t.me/AsmSupport)

---

## 🎧 What is it?

A modern Telegram bot to stream nonstop Radio, Music, and YouTube Lives directly into Group or Channel Voice Chats.

Live in production at:

* 📡 [AsmSafone Channel](https://t.me/AsmSafone)
* 🎵 [AsmSupport Group](https://t.me/AsmSupport)

---

## 🚀 Features

* 🎶 Playlist with queuing and 24/7 radio support
* 🔴 YouTube Live stream support
* 🔁 Auto-fallback to radio when playlist ends
* 🔄 Persistent playback even after Heroku restarts
* ⏱️ Show current audio playback position
* 🕹️ Interactive controls via buttons and commands
* ⬇️ Download audio from YouTube
* 🏷️ Dynamic VC title updates with song name
* ⚡ Pre-download next tracks to ensure smooth playback

---

## ☁ Deploy Instantly

### 💜 Deploy to Heroku

[![Deploy to Heroku](https://img.shields.io/badge/Deploy%20To%20Heroku-blueviolet?style=for-the-badge\&logo=heroku)](https://deploy.safone.tech)

> **Note:** Set Heroku region to **Europe** for better stability.

### ⚡ Deploy to Railway

[![Deploy to Railway](https://img.shields.io/badge/Deploy%20To%20Railway-blueviolet?style=for-the-badge\&logo=railway)](https://railway.app/new/template?template=https%3A%2F%2Fgithub.com%2FAsmSafone%2FRadioPlayerV3&envs=API_ID%2CAPI_HASH%2CBOT_TOKEN%2CSESSION_STRING%2CCHAT_ID%2CLOG_GROUP%2CADMINS%2CADMIN_ONLY%2CMAXIMUM_DURATION%2CSTREAM_URL%2CREPLY_MESSAGE)

> Ensure a voice chat is **started in your group/channel** before deploying.

---

## 🔧 Configuration

### Required ENV Vars

```
API_ID, API_HASH, BOT_TOKEN, SESSION_STRING, CHAT_ID
```

### Optional ENV Vars

```
LOG_GROUP, AUTH_USERS, STREAM_URL, MAXIMUM_DURATION,
REPLY_MESSAGE, ADMIN_ONLY, HEROKU_API_KEY, HEROKU_APP_NAME
```

> [🔗 Live Stream URLs](https://telegra.ph/Live-Radio-Stream-Links-05-17)  |  [⚙️ Generate SESSION\_STRING](https://t.me/genStr_robot)

---

## 📦 Requirements

* Python >= 3.6
* FFmpeg Installed
* Telegram API + String Session
* User Account as Admin in VC

---

## 🖥️ Run Locally (VPS)

```bash
# Install dependencies
sudo apt install git curl python3-pip ffmpeg -y

# Clone & setup
git clone https://github.com/AsmSafone/RadioPlayerV3
cd RadioPlayerV3
pip3 install -r requirements.txt

# Set .env values
# Run the bot
python3 main.py
```

---

## 📄 License

```text
GNU AGPLv3
Copyright (c) 2021  Asm Safone
```

---

## 🙌 Credits

* [@AsmSafone](https://github.com/AsmSafone)
* [@delivrance](https://github.com/delivrance) - Pyrogram
* [@MarshalX](https://github.com/MarshalX) - PyTgCalls
* [All Contributors](https://github.com/AsmSafone/RadioPlayerV3/graphs/contributors)

---
