#!/usr/bin/env python3

#CSCE635 Project
#code structure v1

###############################################################################
#imports
###############################################################################

from math import pi, tau, dist, fabs, cos
# import sys
# import copy
# import numpy as np
# import random
# import queue
# import threading

def rad2deg(x):
    return x * 180 / pi

#clamp x into [m1, m2]
def clamp(x, m1, m2):
    if(x < m1):
        return m1
    if(x > m2):
        return m2
    return x

###############################################################################
#robot controller / state manager
###############################################################################

class RoboController(object):
    """
    robot controller class; contains:
    - robot state machine
    - sensors
    - effectors
    """
    def __init__(self):
        pass

    #loop update function
    #dt is delta time in seconds since last update call
    def update(self, dt):
        pass

###############################################################################  
#sensors
###############################################################################

#proprioception or something
class SensorTimers:
    def __init__(self):
        self.timers = {}

    def start_timer(self, name, time):
        self.timers[name] = time

    #did the timer go off?
    def check_timer_alert(self, name):
        return name in self.timers and self.timers[name] <= 0
    
    #is the timer ticking?
    def check_timer_active(self, name):
        return name in self.timers and self.timers[name] > 0
    
    def stop_timer(self, name):
        if name in self.timers:
            del self.timers[name]

#microphone
#button press
#face detector
#depth detector
#random noise modulator

###############################################################################
#motors and other effectors
###############################################################################

#drive control
#

###############################################################################
#p-field stuff
###############################################################################

###############################################################################
#state machine management
###############################################################################

###############################################################################
#types of states
###############################################################################

###############################################################################
#generic behavior superclass for IRM behaviors
###############################################################################

#deals with behavior releasing/inhibiting
class BehaviorManager(object):
    pass

class GenericBehavior(object):
    def __init__(self, name, controller:RoboController):
        self.name = name
        self.controller = controller
        self.released = False

    def releaser(self):
        return False

    def callback_released(self):
        pass

    def callback_inhibited(self):
        pass

    def update(self, dt):
        pass

###############################################################################
#types of behaviors
###############################################################################

###############################################################################
#main run loop
###############################################################################

if __name__ == '__main__':

    robot = RoboController()
    #parameters
    param_timeout = 120.0 #how long (in seconds) it'll run around before timing out and going back to wander
    #add states and behaviors

    #initial state



    #run loop
    r = rospy.Rate(60)
    t = rospy.get_time()
    while not rospy.is_shutdown():
        dt = rospy.get_time() - t
        t = rospy.get_time()
        robot.update(dt)
        r.sleep()
    # robot.stop()
