FROM debian:latest

# Set non-interactive to avoid hanging on prompts
ENV DEBIAN_FRONTEND=noninteractive

# Combine all updates/installs into one layer
RUN apt update && apt install -y --no-install-recommends \
    git \
    curl \
    python3 \
    python3-pip \
    python3-dev \
    build-essential \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Force-upgrade pip system-wide without touching Debian's apt-managed record file
RUN pip3 install --upgrade pip --ignore-installed --break-system-packages

# Combine regular pip installations to keep layers small
RUN pip3 install -U yt-dlp certifi --break-system-packages

# Copy your local requirements file
COPY requirements.txt /requirements.txt

# ADDED --ignore-installed HERE to bypass the system 'wheel' package block
RUN pip3 install -U -r /requirements.txt --ignore-installed --break-system-packages

# Set up your working directory
RUN mkdir /RadioPlayerV3
WORKDIR /RadioPlayerV3
COPY start.sh /start.sh

# Make sure start.sh is executable
RUN chmod +x /start.sh

# Running Radio Player Bot
CMD ["/bin/bash", "/start.sh"]
