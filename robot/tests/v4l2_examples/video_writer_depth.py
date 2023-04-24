#./capturer_mmap -D /dev/video0 -p 3 -w 480*270 | python video_writer_depth.py 

#./capturer_mmap -D /dev/video0 -p 3 -w 480*270 2>/dev/null | python video_writer_depth.py | sudo python3 py_firmata_test4.py

import cv2
import numpy

from math import floor, pi, sqrt, atan2
from random import random, randrange
from time import time

# https://stackoverflow.com/a/32282458
import sys

# https://stackoverflow.com/a/14981125
def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

w = 480
h = 270
bpp = 2 #bytes per pixel
bpf = w * h * bpp #bytes per frame

def z16_1d_to_u8_2d(arr):
    #convert to w x h x 4 argb
    arr = arr.reshape(h, w)

    # print(arr.shape)
    #discard the bottom ~half, since that has the floor in it
    # h2 = h
    h2 = floor(arr.shape[0] * 0.6)
    arr = arr[:h2, :]
    # print(arr.shape)

    # arr = numpy.concatenate((arr[:,0::2], arr[:,1::2]), axis=1) #every other column

    #testing: convert z16 gray to u8 rgb using gray -> normalized -> some coloration -> u8

    
    arr_dists = numpy.average(arr, axis=0)

    #gray z16 -> normalized gray floats
    arr = arr.astype(numpy.float32)
    arr *= 1/255.0/255.0
    #max over each col
    # arr_min = numpy.min(arr, axis=0)
    arr_avg = numpy.average(arr, axis=0)
    #https://stackoverflow.com/a/53643611
    arr_avg_display = numpy.concatenate([[arr_avg]] * h2, axis=0)
    #bounds
    bound_close = 750 / 255.0 / 255.0 #que units? I think mm
    bound_min = 0
    bound_max = 3000 / 255.0 / 255.0
    # print(arr[0])
    # print(arr.min(), arr.max())
    #color slices
    arr_r = (numpy.interp(arr, [bound_close, bound_max], [1, 0]) * 255.0).astype(numpy.uint8)
    arr_g = (numpy.interp(arr_avg_display, [bound_min, bound_max], [1, 0]) * 255.0).astype(numpy.uint8) #numpy.zeros(arr_r.shape, dtype=numpy.uint8)
    arr_b = (numpy.interp(arr, [bound_close, bound_max], [0, 1]) * 255.0).astype(numpy.uint8)
    #
    # print("r", arr_r.shape)
    # print("g", arr_g.shape)
    # print("b", arr_b.shape)
    #put them together
    arr = numpy.stack((arr_b, arr_g, arr_r), axis=-1)

    # arr = numpy.swapaxes(arr, 0, 1)
    # print(arr.shape)
    
    # print(arr[0][0])

    # arr = numpy.moveaxis(arr, [0, 1, 2], [2, 1, 0])
    # print(arr.shape)
    # print(arr[0][0])

    #convert to w x h x 3 bgr (opencv's preferred format)
    # arr = arr[:,:,1:]
    # print(arr.shape)
    # print(arr[0][0])
    # arr = numpy.flip(arr, 2)
    # print(arr.shape)
    # print(arr[0][0])

    #smh opencv doesn't explicitly support argb are you serious
    #this may not even be better than the above... but whatever
    # arr2 = numpy.ndarray((w, h, 3), dtype=numpy.uint8)
    # cv2.mixChannels([arr], [arr2], [3,0, 2,1, 1,2])

    # print(arr2.shape)
    # print(arr2[0][0])
    # arr2 = numpy.swapaxes(arr2, 0, 1)
    # print(arr2.shape)
    # print(arr2[0][0])

    return (arr, arr_dists)

def deg2rad(deg):
    return pi * deg / 180

#return heading from avg depth value of each camera video column
def calc_heading(arr_avg):
    n = arr_avg.shape[0]
    fov = deg2rad(43) #max angle, in radians, of each side
    indices = numpy.arange(0, n)
    angles = numpy.interp(indices, [0, n - 1], [-fov, fov])
    dist_min = 0
    dist_backup = 750 #750 this seems to be in mm, but needs to have a pretty high threshold
    dist_max = 3000
    mags = numpy.interp(arr_avg, [dist_min, dist_backup, dist_max], [-1, 0, 1])
    #make vectors from mag and rotate by angle, then add them all up
    coses = numpy.cos(angles)
    sines = numpy.sin(angles)
    vecs = numpy.stack((numpy.multiply(mags, coses), numpy.multiply(mags, sines)), axis=-1)
    # print(vecs)
    total = numpy.sum(vecs, axis=0) * (1.0 / n)
    x = total[0]
    y = -total[1] #flip so we turn away from close stuff
    return (x, y)

# cv2.namedWindow("test")

time_rotating = 0
rot_dir = 0

i = 0
prev_time = time()
while(True):
    new_time = time()
    dt = new_time - prev_time
    prev_time = new_time
    # print("frame", i)
    data = sys.stdin.buffer.read(bpf)
    # print("got:", type(data), len(data))
    arr = numpy.frombuffer(data, dtype=numpy.uint16) #.reshape(w, h, bpp)
    # print("in:", arr.shape)
    arr, arr_avg = z16_1d_to_u8_2d(arr)
    #
    # print("out", arr.shape)
    # print(arr[0][0])
    # cv2.imwrite(f"tmp_img_{i}.png", arr)
    #calculate heading from avg distances
    dx = 0
    dy = 0
    if(time_rotating > 0):
        dx = 0
        dy = rot_dir
        time_rotating -= dt
    else:
        dx, dy = calc_heading(arr_avg)
        eprint(dx)
        if(dx < 0.1):
            time_rotating = random() * 3
            rot_dir = 1 if random() < 0.5 else -1
    heading_speed = sqrt(dx * dx + dy * dy)
    heading_angle = atan2(dy, dx)
    print(heading_speed, heading_angle)
    sys.stdout.flush()
    #
    # cv2.imshow("test", arr)
    # cv2.waitKey(1)
    i += 1
    i = i % 10