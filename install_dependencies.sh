#!/bin/bash

# Update and upgrade packages
sudo apt-get update
sudo apt-get upgrade -y

# Install required packages
sudo apt-get install -y python3 python3-pip python3-pil python3-numpy python3-rpi.gpio python3-spidev libatlas-base-dev libopenjp2-7-dev libtiff5-dev zlib1g-dev libfreetype6-dev liblcms2-dev libwebp-dev tcl8.6-dev tk8.6-dev python3-tk libharfbuzz-dev libfribidi-dev libxcb1-dev libjpeg-dev apt-transport-https gnupg1 dirmngr lsb-release

# Install speedtest-cli
curl -L https://packagecloud.io/ookla/speedtest-cli/gpgkey | gpg --dearmor | sudo tee /usr/share/keyrings/speedtestcli-archive-keyring.gpg >/dev/null
echo "deb [signed-by=/usr/share/keyrings/speedtestcli-archive-keyring.gpg] https://packagecloud.io/ookla/speedtest-cli/debian/ $(lsb_release -cs) main" | sudo tee  /etc/apt/sources.list.d/speedtest.list
sudo apt update
sudo apt-get install -y speedtest

# Install waveshare-epd
pip3 install waveshare-epd

# Install the Roboto font
sudo apt-get install -y fonts-roboto
