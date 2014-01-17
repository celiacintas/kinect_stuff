#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import pygame
from myKinect import Kinect

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480

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
        self.myKinect.register()
        #self.ball_manager = BallManager(10)
        # for ball in self.ball_manager.blist:
        #    self.sprites.add(ball)
    
    def onInit(self):
        pygame.init()
        self.display_surf = pygame.display.set_mode(self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)
        self.display_surf.blit(self.background, (0,0))
        self._running = True
        self.myKinect.ctx.start_generating_all()

    def onEvent(self, event):
        if event.type == pygame.QUIT:
            self._running = False

    def onLoop(self):
        self.myKinect.ctx.wait_any_update_all()
        self.myKinect.capture_rgb()
        newpos = self.myKinect.getJoints()
        if newpos:
            #print newpos
            tmp = self.myKinect.depth_generator.to_projective(newpos)
            map(lambda pos: pygame.draw.circle(self.frame, (255, 0, 0),
                              (int(pos[0]), int(pos[1]))
                              , 10, 10), tmp)

    def onRender(self):
        self.sprites.clear(self.display_surf, self.background)
        self.display_surf.blit(self.frame, (0,0))
        #for sprite in self.sprites:
        #        sprite.update()
        #dirty = self.sprites.draw(self.display_surf)
        pygame.display.update()
        pygame.display.flip()

    def onCleanup(self):
        pygame.quit()

    def onExecute(self):
        self.onInit()
        while(self._running):
            for event in pygame.event.get():
                self.onEvent(event)
            self.onLoop()
            self.onRender()
        self.onCleanup()


if __name__ == '__main__':
    theApp = Game()
    theApp.onExecute()
