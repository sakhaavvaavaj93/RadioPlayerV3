#!/bin/bash
export HTTP_PROXY="http://lchnginh:uw1dw5abpert@45.38.107.97:7684"
export HTTPS_PROXY="http://lchnginh:uw1dw5abpert@38.154.203.95:5863"
export ftp_proxy="http://lchnginh:uw1dw5abpert@64.137.96.74:6641"
# ------------------------------

echo "Checking for latest repository updates..."
git init
git remote add origin https://github.com 2>/dev/null || true
git fetch --all
git reset --hard origin/main


echo "Upgrading yt-dlp networking modules..."
/opt/venv/bin/pip install --no-cache-dir -U "yt-dlp[default]" certifi curl-cffi 

#!/bin/bash
echo "Cleaning up workspace..."
rm -rf /RadioPlayerV3

echo "Cloning Repo, Please Wait..."
git clone https://github.com/sakhaavvaavaj93/RadioPlayerV3.git /RadioPlayerV3

echo "Installing Requirements..."
cd /RadioPlayerV3

# Install standard requirements
/opt/venv/bin/pip install --no-cache-dir -U -r requirements.txt

# --- CRITICAL FIX ---
# Update yt-dlp to the latest version to resolve SSL/EOF errors
echo "Updating yt-dlp to latest version..."
/opt/venv/bin/pip install --no-cache-dir -U yt-dlp
# --------------------

echo "Starting Bot, Please Wait..."
/opt/venv/bin/python3 main.py
