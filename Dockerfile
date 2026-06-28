# Debian Based Docker
FROM debian:latest

RUN apt update && apt upgrade -y

# Installing Packages
RUN apt install git curl python3-pip ffmpeg -y

# Installing Pip Packages
RUN pip3 install --upgrade pip

# Crucial: Install/Update yt-dlp explicitly during build
# Adding --break-system-packages in case you are on a modern Debian release
RUN pip3 install -U yt-dlp certifi --break-system-packages

# Copying Requirements
COPY requirements.txt /requirements.txt

# Installing Requirements
RUN pip3 install -U -r /requirements.txt --break-system-packages

RUN mkdir /RadioPlayerV3
WORKDIR /RadioPlayerV3
COPY start.sh /start.sh

# Make sure start.sh is executable
RUN chmod +x /start.sh

# Running Radio Player Bot
CMD ["/bin/bash", "/start.sh"]
