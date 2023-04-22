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

    def update(self, dt):
        for timer in self.timers:
            self.timers[timer] -= dt

#depth detector
#button press
#face detector
#random noise modulator
#microphone (for debug)

###############################################################################
#motors and other effectors
###############################################################################

#drive control
#button led
#face expressions

###############################################################################
#p-field stuff
###############################################################################

###############################################################################
#state machine management
###############################################################################

class StateMachine:
    def __init__(self):
        self.states = [] #states are State objects
        self.transitions = [] #for each State object, store a list of transitions; these are pairs of (predicate, destination state index)
        self.current_state = 0

    def add_state(self, state):
        self.states.append(state)
        self.transitions.append([])
        return len(self.states) - 1 #index of this state

    #add transition from src to dst when predicate is true
    #predicate is a function that takes a robot controller and returns true/false
    def add_transition(self, src_index, predicate, dst_index):
        self.transitions[src_index].append((predicate, dst_index))

    def update(self, robot, dt):
        #update current state
        self.states[self.current_state].update(robot, dt)
        #test for transition
        for t in self.transitions[self.current_state]:
            pred = t[0]
            dst = t[1]
            if(pred(robot)):
                #transition
                self.states[self.current_state].cb_exit(robot)
                self.current_state = dst
                self.states[self.current_state].cb_enter(robot)
                break

class State:
    def __init__(self, name, behaviors, on_enter=None, on_exit=None):
        self.name = name
        self.behaviors = behaviors
        #called when the state is entered
        #start timers, etc
        self.on_enter = on_enter
        #called when the state is exited
        #for cleanup
        self.on_exit = on_exit
        #
    
    def cb_enter(self, robot:RoboController):
        print("Entered state:", self.name)
        if self.on_enter is not None:
            self.on_enter(robot)
    
    def cb_exit(self, robot:RoboController):
        if self.on_exit is not None:
            self.on_exit(robot)
    
    #called every tick that this state is active
    def update(self, robot:RoboController, dt):
        self.behaviors.update(robot, dt)

###############################################################################
#generic behavior manager/superclass for IRM behaviors
###############################################################################

#deals with behavior releasing/inhibiting
class BehaviorManagerIRM(object):
    def __init__(self):
        pass

class GenericBehaviorIRM(object):
    def __init__(self, name):
        self.name = name
        self.released = False

    def releaser(self, robot:RoboController):
        return False

    def callback_released(self, robot:RoboController):
        pass

    def callback_inhibited(self, robot:RoboController):
        pass

    def update(self, robot:RoboController, dt):
        pass

###############################################################################
#generic behavior manager/superclass for sequential behaviors
###############################################################################

#deals with behavior ordering
class BehaviorManagerSeq(object):
    def __init__(self):
        pass

class GenericBehaviorSeq(object):
    def __init__(self, name):
        self.name = name
        self.released = False

    def releaser(self, robot:RoboController):
        return False

    def callback_released(self, robot:RoboController):
        pass

    def callback_inhibited(self, robot:RoboController):
        pass

    def update(self, robot:RoboController, dt):
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


# #when the robot is wandering around, looking for a face
# class StateWander(State):
# #when the robot has found a face and is getting their attention (bump)
# class StateEngage(State):
# #when the robot is running away
# class StatePlay(State):
# #when the robot has been tagged
# class StateSleep(State):
# #just in case
# class StateDebug(State):

    #run loop
    r = rospy.Rate(60)
    t = rospy.get_time()
    while not rospy.is_shutdown():
        dt = rospy.get_time() - t
        t = rospy.get_time()
        robot.update(dt)
        r.sleep()
    # robot.stop()
