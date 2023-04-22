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
        self.states = StateMachine()
        #
        self.gpio = None #TODO
        self.server_connection = None #TODO
        #
        self.sensors = {
            "timers": SensorTimers(),
            "depth": SensorDepth(),
            "button": SensorButtonPress(self.gpio),
            "face": SensorFace(self.server_connection)
        }
        #
        self.effectors = {
            "drive": EffectorDrive(self.gpio),
            "led": EffectorButtonLED(self.gpio),
            "expressions": EffectorExpressions(self.server_connection)
        }

    #loop update function
    #dt is delta time in seconds since last update call
    def update(self, dt):
        self.states.update(self, dt)
        for _, sensor in self.sensors:
            sensor.update(dt)
        for _, effector in self.effectors:
            effector.update(dt)

    #TODO cleanup
    def stop(self):
        for _, sensor in self.sensors:
            sensor.stop()
        for _, effector in self.effectors:
            effector.stop()
        self.gpio.stop()
        self.server_connection.stop()

###############################################################################
#TODO may need a helper class here that redirects gpio stuff to a separate process
#since gpio pin access requires sudo
#and the motor/button classes would just send requests to this class
###############################################################################

###############################################################################
#TODO could use a helper class here
#that manages the pi's connection to the websocket server
#since it's used by 2-3 separate objects: face sensor, sound sensor, expression effector
###############################################################################

###############################################################################  
#sensors
###############################################################################

class Sensor:
    def __init__(self):
        pass

    def update(self, dt):
        pass #update data

    def stop(self):
        pass #for cleanup

#proprioception or something
class SensorTimers(Sensor):
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
class SensorDepth(Sensor):
    def __init__(self):
        self.heading = (0, 0) #speed, angle
        pass #TODO: connect to depth reader subprocess, create polling thread

    def get_heading(self):
        self.heading

    def update(self, dt):
        pass #TODO get most recent heading from polling thread

    def stop(self):
        pass #TODO stop subprocess cleanly

#button press
class SensorButtonPress(Sensor):
    def __init__(self, gpio):
        self.gpio = gpio
        #
        self.down = False #is the button currently down?
        self.pressed = False #was the button previously pressed down? (used to detect taps without repeat)

    def is_down(self):
        return self.down

    def was_clicked(self):
        return self.down and not self.pressed

    def update(self, dt):
        self.pressed = self.down
        self.down = False #TODO update from gpio

#face detector
class SensorFace(Sensor):
    def __init__(self, server_connection):
        self.server_connection = server_connection

    #TODO face API (direction / strength of match?)

    def update(self, dt):
        pass #TODO update data from connection

    def stop(self):
        pass #TODO close connection to server

#random noise modulator
#microphone (for debug)

###############################################################################
#motors and other effectors
###############################################################################

class Effector:
    def __init__(self):
        pass

    def update(self, dt):
        pass #push all effects from within the past loop (e.g. accumulate motor commands)

    def stop(self):
        pass #for cleanup

#drive control / p-field
#takes any number of headings (2d vector of delta x/y) per frame, then accumulates them all
#and generates motor control (speed/direction for both left and right)
#and pushes to gpio
class EffectorDrive(Effector):
    def __init__(self, gpio):
        self.gpio = gpio
        self.heading = (0, 0)

    def push_heading(self, delta):
        prev = self.heading
        self.heading = (prev[0] + delta[0], prev[1] + delta[1])

    def update(self, dt):
        #cap heading to at most 100% speed
        dx = self.heading[0]
        dy = self.heading[1]
        mag = sqrt(dx * dx + dy * dy)
        if(mag > 1):
            dx /= mag
            dy /= mag
        #convert to left/right speed and direction
        heading_speed = sqrt(dx * dx + dy * dy)
        heading_angle = atan2(dy, dx)
        motor_spd_left = heading_speed * cos(heading_angle + pi / 4)
        motor_spd_right = heading_speed * cos(heading_angle - pi / 4)
        #TODO push to motors/gpio
        # motor_left.set_speed(abs(motor_spd_left))
        # motor_left.set_dir(1 if motor_spd_left >= 0 else 0)
        # motor_left.set()
        # motor_right.set_speed(abs(motor_spd_right))
        # motor_right.set_dir(1 if motor_spd_right >= 0 else 0)
        # motor_right.set()

        #clear accumulated heading
        #hypothetically this could also do some running average to smooth out motor commands
        #or it could happen directly in the motor class
        self.heading = (0, 0)

#button led
class EffectorButtonLED(Effector):
    def __init__(self, gpio):
        self.gpio = gpio
        self.value = 0

    def set_led(self, value):
        self.value = value

    def update(self, dt):
        #TODO send led value to gpio

        self.value = 0 #keep light off by default

#face expressions
class EffectorExpressions(Effector):
    def __init__(self, server_connection):
        self.server_connection

    #TODO add functions for the different expressions that the server supports

    def update(self, dt):
        pass #TODO push current expression to server connection object

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
    #predicate is a function that takes the current state and a robot controller and returns true/false
    def add_transition(self, src_index, predicate, dst_index):
        self.transitions[src_index].append((predicate, dst_index))

    def update(self, robot, dt):
        #update current state
        curr = self.states[self.current_state]
        curr.update(robot, dt)
        #test for transition
        for t in self.transitions[self.current_state]:
            pred = t[0]
            dst = t[1]
            if(pred(curr, robot)):
                #transition
                curr.cb_exit(robot)
                self.current_state = dst
                self.states[self.current_state].cb_enter(robot)
                break

class State:
    def __init__(self, name, behaviors, on_enter=None, on_exit=None):
        self.name = name
        self.behaviors = behaviors
        #called when the state is entered
        #start timers, reset behaviors, etc
        self.on_enter = on_enter
        #called when the state is exited
        #for cleanup, disable behaviors, etc
        self.on_exit = on_exit
        #
    
    def cb_enter(self, robot:RoboController):
        print("Entered state:", self.name)
        if self.on_enter is not None:
            self.on_enter(self, robot)
    
    def cb_exit(self, robot:RoboController):
        print("Leaving state:", self.name)
        if self.on_exit is not None:
            self.on_exit(self, robot)
    
    #called every tick that this state is active
    def update(self, robot:RoboController, dt):
        self.behaviors.update(robot, dt)

###############################################################################
#generic behavior manager/superclass for IRM behaviors
###############################################################################

#deals with behavior releasing/inhibiting
class BehaviorManagerIRM(object):
    def __init__(self):
        self.behaviors = []

    def add_behavior(self, behavior:GenericBehaviorIRM):
        self.behaviors.append(behavior)

    def update(self, robot:RoboController, dt):
        for behavior in self.behaviors:
            r = behavior.releaser(robot)
            if(r):
                if(not behavior.released):
                    print(" Releasing %s" % behavior.name)
                    behavior.callback_released(robot)
                else:
                    behavior.update(robot, dt)
            elif((not r) and behavior.released):
                print(" Disabling %s" % behavior.name)
                behavior.callback_inhibited()
            behavior.released = r

    #so when the state is left, all behaviors can be deactivated
    #may not end up using this, tbh
    def disable_all(self):
        for behavior in self.behaviors:
            if(behavior.released)
                print(" *Disabling %s" % behavior.name) #asterisk so we can tell in the log that this is happening
                behavior.callback_inhibited()
                behavior.released = False

#superclass for IRM behaviors
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
        self.index = -1
        self.sequence = [] #a list of seq behaviors that will execute in order

    def add_behavior(self, behavior:GenericBehaviorSeq):
        self.sequence.append(behavior)

    def update(self, robot:RoboController, dt):
        #first update
        if(self.index == -1):
            self.index = 0
            curr = self.sequence[self.index]
            print(" Releasing %s" % curr.name)
            curr.callback_released(robot)
        #later stuff
        elif(self.index < len(self.sequence)):
            curr = self.sequence[self.index]
            curr.update(robot, dt)
            if(curr.is_complete(robot)):
                print(" Disabling %s" % curr.name)
                curr.callback_inhibited(robot)
                self.index += 1
                if(self.index < len(self.sequence)):
                    curr = self.sequence[self.index]
                    print(" Releasing %s" % curr.name)
                    curr.callback_released(robot)
                else:
                    print(" Sequence complete")
    
    #restart the sequence (when the state is entered)
    def restart(self):
        self.index = -1

    #is the sequence done?
    def is_complete(self):
        self.index >= len(self.sequence)

class GenericBehaviorSeq(object):
    def __init__(self, name):
        self.name = name

    def is_complete(self, robot:RoboController):
        return True

    def callback_released(self, robot:RoboController):
        pass

    def callback_inhibited(self, robot:RoboController):
        pass

    def update(self, robot:RoboController, dt):
        pass

###############################################################################
#types of behaviors
###############################################################################

'''
IRMs:
-Move: depth-based navigation
--also needs the turn-around-when-stuck behavior to be built in
-Approach: when a face is detected, add heading towards the face
-Avoid: when a face is detected, add heading away from the face
--may not need this one, since people also register on depth; however, it may be good to give it a stronger avoidance
---but this may cause even more stuck-ness, since it'll potentially re-introduce "corner" cases
"engage" sequence:
-Bump: move towards person and bump them
-turn around: set a random-length timer and a random direction, then turn
'''

###############################################################################
#misc small helpers (enter/exit callbacks and transition predicates)
###############################################################################

#disable all irm behaviors on state exit
def cb_disable_behaviors(state, robot):
    state.behaviors.disable_all()

#restart behavior sequence on state enter
def cb_restart_sequence(state, robot):
    state.behaviors.restart()

#start timer on state enter
def cb_start_timer(name, time):
    return lambda state, robot: robot.sensors["timers"].start_timer(name, time)

#transition if timer goes off
def transition_timeout(name):
    return lambda state, robot: robot.sensors["timers"].check_timer_alert(name)

#transition when behavior sequence is complete
def transition_sequence_complete(state, robot):
    return state.behaviors.is_complete()

#TODO transition from wander -> engage when face is found
def transition_face_found(state, robot):
    return False

#transition from play -> sleep when button is pressed
def transition_tagged(state, robot):
    return robot.sensors["button"].is_down()

###############################################################################
#main run loop
###############################################################################

if __name__ == '__main__':

    robot = RoboController()
    states = robot.states
    #parameters
    param_timeout_play = 20.0 #how long (in seconds) it'll run around before timing out and going back to wander
    param_timeout_sleep = 10.0 #how long it'll sleep before it goes back to wander

    #behaviors (TODO add behaviors to each)
    behaviors_wander = BehaviorManagerIRM()
    behaviors_engage = BehaviorManagerSeq()
    behaviors_play = BehaviorManagerIRM()
    behaviors_sleep = BehaviorManagerIRM() #stays empty

    #states (first is initial state)
    state_wander = State("wander", behaviors_wander, on_exit=cb_disable_behaviors)
    idx_wander = states.add_state(state_wander)
    state_engage = State("engage", behaviors_engage, on_enter=cb_restart_sequence)
    idx_engage = states.add_state(state_engage)
    state_play = State("play", behaviors_play, on_enter=cb_start_timer("timeout_play", param_timeout_play), on_exit=cb_disable_behaviors)
    idx_play = states.add_state(state_play)
    state_sleep = State("sleep", behaviors_sleep, on_enter=cb_start_timer("timeout_sleep", param_timeout_sleep), on_exit=cb_disable_behaviors)
    idx_sleep = states.add_state(state_sleep)
    # state_debug = State("debug", behaviors_debug, on_enter=None, on_exit=None) #TODO we need mic for this

    #state transitions
    states.add_transition(idx_wander, transition_face_found, idx_engage)
    states.add_transition(idx_engage, transition_sequence_complete, idx_play)
    states.add_transition(idx_play, transition_tagged, idx_sleep)
    states.add_transition(idx_play, transition_timeout("timeout_play"), idx_wander)
    states.add_transition(idx_sleep, transition_timeout("timeout_sleep"), idx_wander)

    #run loop
    # r = rospy.Rate(60)
    # t = rospy.get_time()
    # while not rospy.is_shutdown():
    #     dt = rospy.get_time() - t
    #     t = rospy.get_time()
    #     robot.update(dt)
    #     r.sleep()
    # robot.stop()
