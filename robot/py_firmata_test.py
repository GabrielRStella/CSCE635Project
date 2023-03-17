#!/usr/bin/env python3

#https://roboticsbackend.com/control-arduino-with-python-and-pyfirmata-from-raspberry-pi/#Step_1_Run_StandardFirmata_on_your_Arduino_board

import pyfirmata
import time
if __name__ == '__main__':
    board = pyfirmata.Arduino('/dev/ttyACM0')
    print("Communication Successfully started")

    speed = board.digital[5]
    speed.mode = pyfirmata.PWM
    forward = board.digital[7]
    backward = board.digital[8]

    
    d = 0
    s = 0.5
    while True:
        d = 1 - d
        backward.write(d)
        forward.write(1 - d)

        speed.write(s)
        s = s + 0.1
        if(s > 1):
            s = 0.5

        time.sleep(1)

        print("hi", d, s)

        # backward.write(0)
        # forward.write(1)
        # for dc in range(0, 51, 1):
        #     speed.write(dc / 100)
        #     time.sleep(0.1)
        #     print("forward", dc)

        # forward.write(0)
        # backward.write(1)
        # for dc in range(0, 51, 1):
        #     speed.write(dc / 100)
        #     time.sleep(0.1)
        #     print("backward", dc)