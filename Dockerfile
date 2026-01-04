# Debian Based Docker
FROM debian:11-slim

# Update system, install packages, and clean up in one layer
RUN apt update && apt upgrade -y && \
    apt install git curl python3-pip ffmpeg -y && \
    rm -rf /var/lib/apt/lists/* && \
    pip3 install -U pip

# Copying Requirements
COPY requirements.txt /requirements.txt

# Installing Requirements and setting up workspace
RUN pip3 install -U -r requirements.txt && \
    mkdir /RadioPlayerV3

WORKDIR /RadioPlayerV3
COPY start.sh /start.sh

# Running Radio Player Bot
CMD ["/bin/bash", "/start.sh"]
