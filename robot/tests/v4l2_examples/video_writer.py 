#./capturer_mmap -D /dev/video4 -p 2 | python video_writer.py 


import cv2
import numpy

# https://stackoverflow.com/a/32282458
import sys

w = 640
h = 480
bpp = 4 #bytes per pixel (why is "bytes" a keyword???)
bpf = w * h * bpp #bytes per frame

'''
so apparently, from viewer.c, for storing into a 24-bit image for display, the raw image format is:
uint8_t * videoFrame
imageLine1 = (uint8_t *) xImage1->data;
bpl=xImage1->bytes_per_line;
Bpp=xImage1->bits_per_pixel/8;
    imageLine1[(bpl*y)+(Bpp*x)]=videoFrame[(width*4*y)+(4*x)+3];//blue
    imageLine1[(bpl*y)+(Bpp*x)+1]=videoFrame[(width*4*y)+((4*x)+2)];//green
    imageLine1[(bpl*y)+(Bpp*x)+2]=videoFrame[(width*4*y)+((4*x)+1)];//red

so it looks like the data is in 32-bit ARGB, in row-contiguous order
'''

def argb1d_to_bgr2d(arr):
    #convert to w x h x 4 argb
    arr = arr.reshape(h, w, 4)
    print(arr.shape)

    arr = numpy.swapaxes(arr, 0, 1)
    print(arr.shape)
    
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
    arr2 = numpy.ndarray((w, h, 3), dtype=numpy.uint8)
    cv2.mixChannels([arr], [arr2], [3,0, 2,1, 1,2])

    print(arr2.shape)
    print(arr2[0][0])
    arr2 = numpy.swapaxes(arr2, 0, 1)
    print(arr2.shape)
    print(arr2[0][0])
    return arr2

i = 0
while(True):
    print("frame", i)
    data = sys.stdin.buffer.read(bpf)
    print(type(data))
    arr = numpy.frombuffer(data, dtype=numpy.uint8) #.reshape(w, h, bpp)
    print("in:", arr.shape)
    arr = argb1d_to_bgr2d(arr)
    #
    print("out", arr.shape)
    print(arr[0][0])
    cv2.imwrite(f"tmp_img_{i}.png", arr)
    i += 1
    i = i % 10