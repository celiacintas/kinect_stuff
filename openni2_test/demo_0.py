#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import pygame
from pygame.locals import *
from pygame.color import THECOLORS
from primesense import openni2
from primesense import _openni2 as c_api
import numpy as np
import cv
import sys

# array translation take from repo python-openni https://github.com/leezl/OpenNi-Python.git

def translate_frame(frame_data, type):
    """
    need to know what format to get the buffer in:
    if color pixel type is RGB888, then it must be uint8, 
    otherwise it will split the pixels incorrectly
    """
    img  = np.frombuffer(frame_data, dtype=type)
    whatisit = img.size
    if whatisit == (640*480*1):#QVGA
        #shape it accordingly, that is, 1048576=1024*1024
        img.shape = (1, 480, 640)#small chance these may be reversed in certain apis...This order? Really?
        #filling rgb channels with duplicates so matplotlib can draw it (expects rgb)
        img = np.concatenate((img, img, img), axis=0)
        #because the order is so weird, rearrange it (third dimension must be 3 or 4)
        img = np.swapaxes(img, 0, 2)
        img = np.swapaxes(img, 0, 1)
    elif whatisit == (640*480*3):
        #color is miraculously in this order
        img.shape = (480, 640, 3)
    else:
        print "Frames are of size: ",img.size

    return img 


openni2.initialize('/lib/')

dev = openni2.Device.open_any()
depth_stream = dev.create_depth_stream()
depth_stream.set_video_mode(c_api.OniVideoMode(pixelFormat = c_api.OniPixelFormat.ONI_PIXEL_FORMAT_DEPTH_100_UM, resolutionX = 640, resolutionY = 480, fps = 30))
depth_stream.start()

pygame.init()
screen = pygame.display.set_mode((640, 480))
ir_frame = pygame.Surface((640, 480))
pygame.display.set_caption('Structure Map')

running = True

while running:
    for event in pygame.event.get():
        if event.type == KEYDOWN and event.key == K_ESCAPE: running = False

    frame = depth_stream.read_frame()
    frame_data = frame.get_buffer_as_uint16()

    frame_surface = pygame.transform.rotate(pygame.transform.flip(pygame.surfarray.make_surface(translate_frame(frame_data, np.uint16)), True, False), 90)
    ir_frame.blit(frame_surface, (0, 0))
    screen.blit(ir_frame, (0, 0))

    pygame.display.flip()

depth_stream.stop()
openni2.unload()

sys.exit(0)