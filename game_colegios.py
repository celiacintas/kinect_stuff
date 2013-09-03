#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import openni
import pygame 
import numpy as np
from cv2 import cv

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480

class Ball(pygame.sprite.Sprite):
    """Ball Class for set image, speed and velocity """
    def __init__(self, xy, speed, angle):
        pygame.sprite.Sprite.__init__(self)
        self.img_load('../images/sphere.png')
        self.rect.centerx, self.rect.centery = xy
        self.speed =  speed
        self.angle = angle
        
    def move(self):
        self.rect.centerx += np.sin(self.angle) * self.speed
        self.rect.centery -= np.cos(self.angle) * self.speed
        
    def bounce(self):
        if self.rect.centerx > SCREEN_WIDTH - self.rect.width:
            self.rect.centerx = 2*(SCREEN_WIDTH - self.rect.width) - self.rect.centerx
            self.angle = -self.angle*2
        elif self.rect.centerx < self.rect.width:
            self.rect.centerx = 2*self.rect.width - self.rect.centerx
            self.angle = -self.angle*2
        if self.rect.centery > SCREEN_HEIGHT - self.rect.height:
            self.rect.centery = 2*(SCREEN_HEIGHT - self.rect.height) - self.rect.centery
            self.angle = np.pi - self.angle*2    
        elif self.rect.centery < self.rect.height:
            self.rect.centery = 2*self.rect.width - self.rect.centery
            self.angle = np.pi - self.angle*2
        
    def img_load(self, filename):
        self.image = pygame.image.load(filename)
        self.image = pygame.transform.scale(self.image, (60,60))  
        self.rect = self.image.get_rect()
        

class BallManager:
    """ Create and update state of balls"""
    def __init__(self, numballs = 30, balls = []):      
        self.blist = balls
        self.multipleBalls(numballs)

    def update(self):
        for ball in self.blist:
            ball.move()
            ball.bounce()

    def add_ball(self, xy, speed, angle):
        self.blist.append(Ball(xy, speed, angle))

    def multipleBalls(self, numballs):
        for i in range(numballs):
            self.add_ball((np.random.randint(0, SCREEN_WIDTH),
                          np.random.randint(0, SCREEN_HEIGHT)),
                          np.random.randint(4, 6),
                          np.random.uniform(0, np.pi*2))
class Kinect:
    """Manage context and generator of the kinect"""
    def __init__(self, game):

        self.context = openni.Context()
        self.context.init()
        self.depth_generator = openni.DepthGenerator()
        self.depth_generator.create(self.context)
        self.depth_generator.set_resolution_preset(openni.RES_VGA)
        self.depth_generator.fps = 30

        self.image_generator = openni.ImageGenerator()
        self.image_generator.create(self.context)
        self.image_generator.set_resolution_preset(openni.RES_VGA)
        
        self.gesture_generator = openni.GestureGenerator()
        self.gesture_generator.create(self.context)
        self.gesture_generator.add_gesture('Wave')
        
        self.hands_generator = openni.HandsGenerator()
        self.hands_generator.create(self.context)

        self.gesture_generator.register_gesture_cb(self.gesture_detected, self.gesture_progress)
        self.hands_generator.register_hand_cb(self.create, self.update, self.destroy)

        self.game = game 

    def gesture_detected(self, src, gesture, id, end_point):
        print "Detected gesture:", gesture
        self.hands_generator.start_tracking(end_point)

    def gesture_progress(self, src, gesture, point, progress): 
        pass

    def destroy(self, src, id, time): 
        pass

    def create(self, src, id, pos, time): 
        pass

    def update(self, src, id, pos, time):
        if pos != None:
            for ball in self.game.ball_manager.blist:
                new_rect = pygame.Rect(int(ball.rect.x), int(ball.rect.y), 60, 60)
                kinect_rect = pygame.Rect(self.game.size[0]/2 - int(pos[0]), self.game.size[1]/2 - int(pos[1]), 40, 40)
                print "kinect %s and ball %s" %(kinect_rect.center, new_rect.center)
                if new_rect.colliderect(kinect_rect):
                    print "wiii %d" %(len(self.game.ball_manager.blist))
                    ball.kill()
            pygame.draw.circle(self.game.display_surf, (0, 128, 255), (self.game.size[0]/2 - int(pos[0]), self.game.size[1]/2 - int(pos[1])), 10)


    def capture_rgb(self):
        rgb_frame = np.fromstring(self.image_generator.get_raw_image_map_bgr(), dtype=np.uint8).reshape(SCREEN_HEIGHT, SCREEN_WIDTH, 3)
        image = cv.fromarray(rgb_frame)
        cv.Flip(image, None, 1)
        cv.CvtColor(cv.fromarray(rgb_frame), image, cv.CV_BGR2RGB)
        self.game.frame = pygame.image.frombuffer(image.tostring(), cv.GetSize(image), 'RGB')


class Game:
    """Define screen, sprites and states of the game"""
    def __init__(self):
        self.timer = pygame.time.Clock()
        self.sprites = pygame.sprite.RenderUpdates()
        self._running = True
        self.display_surf = None
        self.background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.background.fill((0,0,0))
        self.size = (SCREEN_WIDTH, SCREEN_HEIGHT)
        self.frame = None
        self.myKinect = Kinect(self)
        self.ball_manager = BallManager(100)
        for ball in self.ball_manager.blist:
            self.sprites.add(ball)

    def on_init(self):
        pygame.init()
        self.display_surf = pygame.display.set_mode(self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)
        self.display_surf.blit(self.background, (0,0))
        self._running = True
        self.myKinect.context.start_generating_all()

    def on_event(self, event):
        if event.type == pygame.QUIT:
            self._running = False

    def on_loop(self):        
        self.myKinect.context.wait_any_update_all()
        self.myKinect.capture_rgb()
        self.ball_manager.update()

    def on_render(self):
        self.sprites.clear(self.display_surf, self.background)
        self.display_surf.blit(self.frame, (0,0))
        for sprite in self.sprites:
                sprite.update()
        dirty = self.sprites.draw(self.display_surf)
        pygame.display.update(dirty)
        pygame.display.flip()

    def on_cleanup(self):
        pygame.quit()
 
    def on_execute(self):
        self.on_init()
        while( self._running ):
            for event in pygame.event.get():
                self.on_event(event)
            self.on_loop()
            self.on_render()
        self.on_cleanup()


if __name__ == '__main__':
    theApp = Game()
    theApp.on_execute()

