
/*
realsense:
video0 = depth
video2 = infrared
video4 = rgb

python attempt (can't load Z16 format of depth stream):

import cv2
from cv2 import VideoCapture, imwrite
import numpy
cap = cv2.VideoCapture(4)
b, frame = cap.read()
cv2.imwrite("tmp_img.png", frame)

cmdline video device info (replace 2 with any device number):

v4l2-ctl -d0 --list-formats-ext
v4l2-ctl -d2 --list-formats-ext
v4l2-ctl -d4 --list-formats-ext
*/

//from jeff and chatgpt, with modifications by G
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <linux/videodev2.h>

int main()
{
    printf("Starting program\n\n");

    
    const char* device = "/dev/video4";
    printf("Opening device \"%s\"\n", device);
    // Open the video device file for reading
    int fd = open(device, O_RDWR);
    if (fd == -1) {
        perror("Failed to open device");
        exit(EXIT_FAILURE);
    }
    printf(" Done\n");

    printf("Querying video capabilities...\n");
    // Query the device capabilities
    struct v4l2_capability cap;
    if (ioctl(fd, VIDIOC_QUERYCAP, &cap) == -1) {
        perror("Failed to query device capabilities");
        exit(EXIT_FAILURE);
    }
    printf(" Done\n");

    printf("Setting format...\n");
    // Set the video format
    struct v4l2_format fmt;
    fmt.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    fmt.fmt.pix.width = 640;
    fmt.fmt.pix.height = 480;
    fmt.fmt.pix.pixelformat = V4L2_PIX_FMT_YUYV; //hmmm V4L2_PIX_FMT_Z16 V4L2_PIX_FMT_SGRBG16
    fmt.fmt.pix.field = V4L2_FIELD_NONE;
    printf(" Size: %dx%d\n", fmt.fmt.pix.width, fmt.fmt.pix.height);
    if (ioctl(fd, VIDIOC_S_FMT, &fmt) == -1) {
        perror("Failed to set video format");
        exit(EXIT_FAILURE);
    }
    printf(" Done\n");

    printf(" Requesting video buffers...\n");
    // Request video buffers
    struct v4l2_requestbuffers req;
    req.count = 4;
    req.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    req.memory = V4L2_MEMORY_MMAP;
    if (ioctl(fd, VIDIOC_REQBUFS, &req) == -1) {
        perror("Failed to request video buffers");
        exit(EXIT_FAILURE);
    }
    printf(" Done\n");

    printf(" Mapping video buffers...\n");
    // Map the video buffers
    struct v4l2_buffer buf;
    void* buffer;
    for (int i = 0; i < req.count; i++) {
        printf(" %d/%d\n", i+1, req.count);
        buf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
        buf.memory = V4L2_MEMORY_MMAP;
        buf.index = i;
        if (ioctl(fd, VIDIOC_QUERYBUF, &buf) == -1) {
            perror("Failed to query video buffer");
            exit(EXIT_FAILURE);
        }
        buffer = mmap(NULL, buf.length, PROT_READ | PROT_WRITE, MAP_SHARED, fd, buf.m.offset);
        if (buffer == MAP_FAILED) {
            perror("Failed to map video buffer");
            exit(EXIT_FAILURE);
        }
    }
    printf(" Done\n");

    printf(" Starting video capture...\n");
    // Start capturing video
    enum v4l2_buf_type type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    if (ioctl(fd, VIDIOC_STREAMON, &type) == -1) {
        perror("Failed to start video capture");
        exit(EXIT_FAILURE);
    }
    printf(" Done\n");

    printf(" Entering stream loop\n");
    // Read video data
    while (1) {
        fd_set fds;
        struct timeval tv;
        int r;

        FD_ZERO(&fds);
        FD_SET(fd, &fds);

        tv.tv_sec = 2;
        tv.tv_usec = 0;

        printf(" Waiting for select...\n");
        r = select(fd + 1, &fds, NULL, NULL, &tv);
        if (r == -1) {
            perror("select");
            break;
        }
        if (r == 0) {
            printf("select timeout\n");
            continue;
        }
        printf("  Passed\n");

        printf(" Dequeuing buffer...\n");
        buf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
        buf.memory = V4L2_MEMORY_MMAP;
        if (ioctl(fd, VIDIOC_DQBUF, &buf) == -1) {
            perror("Failed to dequeue video buffer");
            exit(EXIT_FAILURE);
        }
        printf("  Done\n");

        // Process video data here
        printf("got frame\n");
    }

    printf("\nExiting program\n");
}