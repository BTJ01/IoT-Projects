# -*- coding: utf-8 -*-
# Import Python System Libraries
import time
import json
import subprocess

# Import Requests Library
import requests

#Import Blinka
import digitalio
import board

# Import Python Imaging Library
from PIL import Image, ImageDraw, ImageFont
from adafruit_rgb_display.rgb import color565
import adafruit_rgb_display.st7789 as st7789

api_url = 'http://localhost/admin/api.php'

# Configuration for CS and DC pins (these are FeatherWing defaults on M0/M4):
cs_pin = digitalio.DigitalInOut(board.CE0)
dc_pin = digitalio.DigitalInOut(board.D25)
reset_pin = None

# Config for display baudrate (default max = 24mhz, Pi can do better!):
BAUDRATE = 64000000

# Create the ST7789 display:
disp = st7789.ST7789(
    board.SPI(), # Setup SPI bus using hardware SPI
    cs=cs_pin, 
    dc=dc_pin, 
    rst=reset_pin, 
    baudrate=BAUDRATE,
    width=135, 
    height=240, 
    x_offset=53, 
    y_offset=40)

# Create blank image for drawing.
# Make sure to create image with mode 'RGB' for full color.
height = disp.width   # we swap height/width to rotate it to landscape!
width = disp.height
image = Image.new('RGB', (width, height))
rotation = 90

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0, 0, width, height), outline=0, fill=0)
disp.image(image, rotation)

# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
padding = -2
top = padding
bottom = height-padding

# Move left to right keeping track of the current x position for drawing shapes.
x = 0


# Alternatively load a TTF font.  Make sure the .ttf font file is in the
# same directory as the python script!
# Some other nice fonts to try: http://www.dafont.com/bitmap.php
font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 24)

# Turn on the backlight
backlight = digitalio.DigitalInOut(board.D22)
backlight.switch_to_output()


# Add buttons as inputs
buttonA = digitalio.DigitalInOut(board.D23)
buttonB = digitalio.DigitalInOut(board.D24)
buttonA.switch_to_input()
buttonB.switch_to_input()


while True:
    # Shell scripts for system monitoring from here:
    # https://unix.stackexchange.com/questions/119126/command-to-display-memory-usage-disk-usage-and-cpu-load
    cmd = "hostname -I | cut -d\' \' -f1"
    IP = "IP: "+subprocess.check_output(cmd, shell=True).decode("utf-8")
    cmd = "hostname | tr -d \'\\n\'"
    HOST = subprocess.check_output(cmd, shell=True).decode("utf-8")
    cmd = "top -bn1 | grep load | awk '{printf \"CPU Load: %.2f\", $(NF-2)}'"
    CPU = subprocess.check_output(cmd, shell=True).decode("utf-8")
    cmd = "free -m | awk 'NR==2{printf \"%s/%s MB  %.2f%%\", $3,$2,$3*100/$2 }'"
    MemUsage = subprocess.check_output(cmd, shell=True).decode("utf-8")
    cmd = "df -h | awk '$NF==\"/\"{printf \"Disk: %d/%d GB  %s\", $3,$2,$5}'"
    Disk = subprocess.check_output(cmd, shell=True).decode("utf-8")
    cmd = "cat /sys/class/thermal/thermal_zone0/temp |  awk \'{printf \"CPU Temp: %.1f C\", $(NF-0) / 1000}\'" # pylint: disable=line-too-long
    Temp = subprocess.check_output(cmd, shell=True).decode("utf-8")

    # Pi Hole data!
    try:
        r = requests.get(api_url)
        data = json.loads(r.text)
        DNSQUERIES = data['dns_queries_today']
        ADSBLOCKED = data['ads_blocked_today']
        CLIENTS = data['unique_clients']
    except KeyError:
        time.sleep(1)
        continue

    y = top
    if buttonA.value and buttonB.value:  # no buttons pressed
        draw.rectangle((0, 0, width, height), outline=0, fill=0)
        backlight.value = False  # turn off backlight
    
    elif buttonA.value and not buttonB.value:  # just button B pressed
        draw.rectangle((0, 0, width, height), outline=0, fill=(30, 45, 60))
        backlight.value = True
        # draw.text((x, y), IP, font=font, fill="#C0C0C0")
        # y += font.getsize(IP)[1]
        draw.text((x, y), CPU, font=font, fill="#FF9800")
        y += font.getsize(CPU)[1]
        draw.text((x, y), "Memory:", font=font, fill="#26A69A")
        y += font.getsize(MemUsage)[1]
        draw.text((x, y), MemUsage, font=font, fill="#26A69A")
        y += font.getsize(MemUsage)[1]
        draw.text((x, y), Disk, font=font, fill="#9575CD")
        y += font.getsize(Disk)[1]
        draw.text((x, y), Temp, font=font, fill="#EF5350")
        # y += font.getsize(Disk)[1]
        # draw.text((x, y), "DNS Queries: {}".format(DNSQUERIES), font=font, fill="#FF00FF")
    
    elif buttonB.value and not buttonA.value:  # just button A pressed
        draw.rectangle((0, 0, width, height), outline=0, fill=(30, 45, 60))
        backlight.value = True
        draw.text((x, y), "Pi-Hole", font=font, fill="#C0C0C0")
        y += font.getsize(HOST)[1]
        draw.text((x, y), IP, font=font, fill="#FF9800")
        y += font.getsize(IP)[1]
        draw.text((x, y), "Ads Blocked: {}".format(str(ADSBLOCKED)), font=font, fill="#26A69A")
        y += font.getsize(str(ADSBLOCKED))[1]
        draw.text((x, y), "Clients: {}".format(str(CLIENTS)), font=font, fill="#9575CD")
        y += font.getsize(str(CLIENTS))[1]
        draw.text((x, y), "DNS Queries: {}".format(str(DNSQUERIES)), font=font, fill="#EF5350")
        y += font.getsize(str(DNSQUERIES))[1]
    
    else:
        draw.rectangle((0, 0, width, height), outline=0, fill=0)
        backlight.value = False

    # Display image.
    disp.image(image, rotation)
    time.sleep(.1)
