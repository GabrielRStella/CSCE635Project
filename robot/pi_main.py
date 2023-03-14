# NOTE: from Jeff
    # putting this code here so I don't loose it


# Pinout:
    # ,--------------------------------.
    # | oooooooooooooooooooo J8     +====
    # | 1ooooooooooooooooooo        | USB
    # |                             +====
    # |      Pi Model 3B  V1.2         |
    # |      +----+                 +====
    # | |D|  |SoC |                 | USB
    # | |S|  |    |                 +====
    # | |I|  +----+                    |
    # |                   |C|     +======
    # |                   |S|     |   Net
    # | pwr        |HDMI| |I||A|  +======
    # `-| |--------|    |----|V|-------'

    # Revision           : a22082
    # SoC                : BCM2837
    # RAM                : 1024Mb
    # Storage            : MicroSD
    # USB ports          : 4 (excluding power)
    # Ethernet ports     : 1
    # Wi-fi              : True
    # Bluetooth          : True
    # Camera ports (CSI) : 1
    # Display ports (DSI): 1

    # J8:
    #    3V3  (1) (2)  5V    
    #  GPIO2  (3) (4)  5V    
    #  GPIO3  (5) (6)  GND   
    #  GPIO4  (7) (8)  GPIO14
    #    GND  (9) (10) GPIO15
    # GPIO17 (11) (12) GPIO18
    # GPIO27 (13) (14) GND   
    # GPIO22 (15) (16) GPIO23
    #    3V3 (17) (18) GPIO24
    # GPIO10 (19) (20) GND   
    #  GPIO9 (21) (22) GPIO25
    # GPIO11 (23) (24) GPIO8 
    #    GND (25) (26) GPIO7 
    #  GPIO0 (27) (28) GPIO1 
    #  GPIO5 (29) (30) GND   
    #  GPIO6 (31) (32) GPIO12
    # GPIO13 (33) (34) GND   
    # GPIO19 (35) (36) GPIO16
    # GPIO26 (37) (38) GPIO20
    #    GND (39) (40) GPIO21

import RPi.GPIO as GPIO
import time

pwm1_out = 32 # GPIO 12

GPIO.setmode(GPIO.BOARD)
GPIO.setup(pwm1_out, GPIO.OUT)
GPIO.output(pwm1_out, GPIO.LOW)
pwm = GPIO.PWM(pwm1_out, 1000)
pwm.stop()
pwm.start(0)

def loop():
    while True:
        for dc in range(0, 101, 1):
            pwm.ChangeDutyCycle(dc)
            time.sleep(0.01)
        
        time.sleep(1)
        
        for dc in range(100, -1, -1):
            pwm.ChangeDutyCycle(dc)
            time.sleep(0.01)
        
        time.sleep(1)

def destroy():
    pwm.stop()
    GPIO.output(pwm1_out, GPIO.LOW)
    GPIO.cleanup()

loop()