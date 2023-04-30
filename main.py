#!/usr/bin/python3
# -*- coding:utf-8 -*-
import os
import socket
import fcntl
import struct
import subprocess
import logging
from PIL import Image, ImageDraw, ImageFont
from waveshare_epd import epd2in7_V2
import time
import re

logging.basicConfig(level=logging.DEBUG)

script_dir = os.path.dirname(os.path.realpath(__file__))
font_dir = os.path.join(script_dir, "fonts")

def get_ip_address(ifname):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        return socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s', ifname[:15].encode('utf-8')))[20:24])

def get_wifi_info():
    try:
        ssid = subprocess.check_output(["iwgetid", "-r"]).decode("utf-8").strip()
        signal_strength = int(subprocess.check_output(["iwconfig", "wlan0"]).decode("utf-8").split('Signal level=')[1].split(' ')[0].strip())
        return ssid, signal_strength
    except Exception as e:
        logging.error(f"Error getting Wi-Fi info: {e}")
        return None, None

def create_image(epd, ip_address, ssid, signal_strength, ping, download, upload, jitter, fonts):
    Limage = Image.new('1', (epd.height, epd.width), 255)
    draw = ImageDraw.Draw(Limage)

    font = fonts['Roboto-Regular']
    font_small = ImageFont.truetype(os.path.join(font_dir, 'Roboto-Regular.ttf'), 14)

    # Draw IP address
    ip_address_width, ip_address_height = draw.textsize(ip_address, font=font)
    ip_address_x = (epd.width - ip_address_width) // 2
    draw.text((ip_address_x, 5), ip_address, font=font, fill=0)

    # Draw SSID
    ssid_width, ssid_height = draw.textsize(ssid, font=font)
    ssid_x = (epd.width - ssid_width) // 2
    draw.text((ssid_x, 25), ssid, font=font, fill=0)

    # Draw signal strength bar
    bar_width = 150
    bar_height = 20
    bar_x = (epd.width - bar_width) // 2
    bar_y = 50
    draw.rectangle([bar_x, bar_y, bar_x + bar_width, bar_y + bar_height], outline=0)

    filled_width = int(bar_width * min(max((signal_strength + 90) / 60, 0), 1))
    draw.rectangle([bar_x, bar_y, bar_x + filled_width, bar_y + bar_height], fill=0)

    # Draw signal strength label
    if signal_strength >= -30:
        label = "Amazing"
    elif signal_strength >= -67:
        label = "Very Good"
    elif signal_strength >= -70:
        label = "Okay"
    else:
        label = "Poor"

    label_width, label_height = draw.textsize(label, font=font)
    label_x = (epd.width - label_width) // 2
    draw.text((label_x, 70), label, font=font, fill=0)

    # Draw speedtest results
    speedtest_y = 100
    draw.text((10, speedtest_y), f"Ping: {ping} ms", font=font_small, fill=0)
    draw.text((10, speedtest_y + 20), f"Download: {download} Mbps", font=font_small, fill=0)
    draw.text((10, speedtest_y + 40), f"Upload: {upload} Mbps", font=font_small, fill=0)
    draw.text((10, speedtest_y + 60), f"Jitter: {jitter} ms", font=font_small, fill=0)

    return Limage

def get_speedtest_info():
    response = subprocess.Popen('/usr/bin/speedtest --accept-license --accept-gdpr', shell=True, stdout=subprocess.PIPE).stdout.read().decode('utf-8')

    ping = re.search('Latency:\s+(.*?)\s', response, re.MULTILINE)
    download = re.search('Download:\s+(.*?)\s', response, re.MULTILINE)
    upload = re.search('Upload:\s+(.*?)\s', response, re.MULTILINE)
    jitter = re.search('Latency:.*?jitter:\s+(.*?)ms', response, re.MULTILINE)

    ping = ping.group(1) if ping else None
    download = download.group(1) if download else None
    upload = upload.group(1) if upload else None
    jitter = jitter.group(1) if jitter else None

    return ping, download, upload, jitter

def main():
    try:
        epd = epd2in7_V2.EPD()
        epd.init()

        ip_address = get_ip_address('wlan0')

        script_dir = os.path.dirname(os.path.realpath(__file__))
        font_dir = os.path.join(script_dir, "fonts")
        fonts = {}
        fonts['Roboto-Regular'] = ImageFont.truetype(os.path.join(font_dir, 'Roboto-Regular.ttf'), 20)

        while True:
            ssid, signal_strength = get_wifi_info()
            ping, download, upload, jitter = get_speedtest_info()

            if ssid is not None and signal_strength is not None and ping is not None and download is not None and upload is not None and jitter is not None:
                Limage = create_image(epd, ip_address, ssid, signal_strength, ping, download, upload, jitter, fonts)

                logging.info("Full Refresh")
                epd.init()
                logging.info("Drawing on the image...")
                epd.display_Base(epd.getbuffer(Limage))
                epd.sleep()

                time.sleep(60*60)  # Refresh every hour

    except IOError as e:
        logging.error("IOError: ", e)

    except KeyboardInterrupt:
        logging.info("ctrl + c:")
        epd2in7_V2.epdconfig.module_exit()
        exit()

if __name__ == '__main__':
    main()
