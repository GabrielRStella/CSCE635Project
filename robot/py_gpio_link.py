#!/usr/bin/env python3

#https://roboticsbackend.com/control-arduino-with-python-and-pyfirmata-from-raspberry-pi/#Step_1_Run_StandardFirmata_on_your_Arduino_board

#sudo python3 py_firmata_test4.py 


import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)
GPIO.setup(11, GPIO.IN, GPIO.PUD_UP)

from math import pi, cos, sin

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

import pyfirmata
import time
if __name__ == '__main__':
    board = pyfirmata.Arduino('/dev/ttyACM0')
    print("Communication Successfully started")

    motor_left = Motor(board, 5, 7, 8)
    motor_right = Motor(board, 6, 11, 9)

    moving = 0
    pressing = False
    
    while True:
        #
        i = GPIO.input(11)
        b = (i < 0.5)
        if(b):
            if(not pressing):
                pressing = True
                moving = 1 - moving
        else:
            pressing = False
        #input heading from stdin
        line = input()
        vals = line.split(" ")
        # print("got", vals)
        heading_speed = float(vals[0])
        heading_angle = float(vals[1])
        #
        motor_spd_left = moving * heading_speed * cos(heading_angle + pi / 4)
        motor_spd_right = moving * heading_speed * cos(heading_angle - pi / 4)
        #

        motor_left.set_speed(abs(motor_spd_left))
        motor_left.set_dir(1 if motor_spd_left >= 0 else 0)
        motor_left.set()

        motor_right.set_speed(abs(motor_spd_right))
        motor_right.set_dir(1 if motor_spd_right >= 0 else 0)
        motor_right.set()