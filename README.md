# Pi-Projects

A place to keep track of things used in my Raspberry Pi Projects

## Projects

#### Pi Zero W + PiTFT:
1. Pi-Hole Ad-Blocker
  * Stats.py - tweaked script from AdaFruit ([found here](https://learn.adafruit.com/pi-hole-ad-blocker-with-pi-zero-w/install-mini-pitft "Pi-Hole Ad-Blocker: Install Mini PiTFT")) to adjust stats display to my liking
    - changed `HOST` to display "Pi-Hole", moved to first line
    - changed font colors
    - removed `IP` & `DNS Queries` from screen2
    - added `CPU Temp` to screen2
    - changed `Mem:` to `Memory:` and moved values to new line to fix off screen text
    - set backlight off, screen black when no buttons are pressed
    - set top button to display screen1, bottom button to display screen2
    - calculations don't run until a button is pressed
  
2. Unbound Recursive DNS Resolver
