#!/usr/bin/env python3

#https://roboticsbackend.com/control-arduino-with-python-and-pyfirmata-from-raspberry-pi/#Step_1_Run_StandardFirmata_on_your_Arduino_board

#sudo python3 py_firmata_test4.py 


import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)
GPIO.setup(11, GPIO.IN, GPIO.PUD_UP)

from math import pi, cos, sin

import sys

#motor pins:
#5 = left speed (PWM)
#7 = left forwards
#8 = left backwards
#6 = right speed (PWM)
#11 = right forwards
#9 = right backwards
class Motor:
    def __init__(self, board, speed_pin_no, forward_pin_no, backward_pin_no):
        self.speed_pin = board.digital[speed_pin_no]
        self.speed_pin.mode = pyfirmata.PWM
        self.forward_pin = board.digital[forward_pin_no]
        self.backward_pin = board.digital[backward_pin_no]
        #
        self.spd = 0 #range 0-1
        self.direction = 1 #1 = forward, 0 = backward

    #spd in range 0 to 1
    #note anything less than 0.5 is rounded up to prevent motor issues
    #unless it's zero, which disables motors
    def set_speed(self, spd):
        if(0 < spd and spd < 0.5):
            spd = 0.5
        self.spd = spd
    
    def set_dir(self, d):
        if(d < 0.5):
            d = 0
        else:
            d = 1
        self.direction = d

    def set(self):
        # print(self.spd)
        if(self.spd == 0):
            self.speed_pin.write(0)
            self.forward_pin.write(0)
            self.backward_pin.write(0)
        else:
            self.speed_pin.write(self.spd)
            self.forward_pin.write(self.direction)
            self.backward_pin.write(1 - self.direction)
            #oops we mounted the motors backward
            # self.forward_pin.write(1 - self.direction)
            # self.backward_pin.write(self.direction)

# https://stackoverflow.com/a/14981125
def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

import pyfirmata
import time

if __name__ == '__main__':
    eprint("Connecting to arduino...")
    board = pyfirmata.Arduino('/dev/ttyACM0')
    eprint(" connected!")

    motor_left = Motor(board, 5, 7, 8)
    motor_right = Motor(board, 6, 11, 9)

    moving = 0
    btn_was_down = False

    # eprint("hi...")
    # first_line = input() #skip one line
    # eprint("bye:", first_line)
    
    while True:
        #
        i = GPIO.input(11)
        #input command from stdin
        line = input()
        vals = line.split(" ")
        #
        cmd = int(vals[0])
        # eprint("processing:", vals)
        match(cmd):
            #input
            case -1:
                i = GPIO.input(11)
                btn_down = (i < 0.5)
                #send result
                print(str(btn_down) + " " + str(btn_was_down))
                #update for next loop
                btn_was_down = btn_down
            #left motor
            case 0:
                motor_spd_left = float(vals[1])
                motor_left.set_speed(abs(motor_spd_left))
                motor_left.set_dir(1 if motor_spd_left >= 0 else 0)
                motor_left.set()
                print("Done: left motor") #notify main process
            #right motor
            case 1:
                motor_spd_right = float(vals[1])
                motor_right.set_speed(abs(motor_spd_right))
                motor_right.set_dir(1 if motor_spd_right >= 0 else 0)
                motor_right.set()
                print("Done: right motor") #notify main process
        sys.stdout.flush()