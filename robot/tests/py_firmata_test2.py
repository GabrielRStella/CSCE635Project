#!/usr/bin/env python3

#https://roboticsbackend.com/control-arduino-with-python-and-pyfirmata-from-raspberry-pi/#Step_1_Run_StandardFirmata_on_your_Arduino_board


import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)
GPIO.setup(11, GPIO.IN, GPIO.PUD_UP)


import pyfirmata
import time
if __name__ == '__main__':
    board = pyfirmata.Arduino('/dev/ttyACM0')
    print("Communication Successfully started")

    speed = board.digital[5]
    speed.mode = pyfirmata.PWM
    forward = board.digital[7]
    backward = board.digital[8]

    
    while True:
        #
        i = GPIO.input(11)
        b = (i > 0.5)
        #
        d = 1 if b else 0
        s = 0.5

        backward.write(d)
        forward.write(1 - d)

        speed.write(s)

        time.sleep(0.01)