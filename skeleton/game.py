#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import pygame
from mykinect import Kinect

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480


class Game(object):

    """Define screen and states of the game"""

    def __init__(self):
        """Setup the display and configure the kinect
        for the game."""
        self.timer = pygame.time.Clock()
        self.sprites = pygame.sprite.RenderUpdates()
        self._running = True
        self.display_surf = None
        self.background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.background.fill((0, 0, 0))
        self.size = (SCREEN_WIDTH, SCREEN_HEIGHT)
        self.frame = None
        self.my_kinect = Kinect(self)
        self.my_kinect.register()

    def on_init(self):
        """Initialize kinect and display"""
        pygame.init()
        self.display_surf = pygame.display.set_mode(
            self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)
        self.display_surf.blit(self.background, (0, 0))
        self._running = True
        self.my_kinect.ctx.start_generating_all()

    def on_event(self, event):
        """Event management"""
        if event.type == pygame.QUIT:
            self._running = False

    def on_loop(self):
        """Update frame from kinect and display
        new joints."""
        self.my_kinect.update_sensor()
        self.my_kinect.capture_rgb()
        newpos_skeleton = self.my_kinect.get_joints()
        if newpos_skeleton:
            map(lambda pos: pygame.draw.circle(self.frame, (255, 50, 0),
               (int(pos[0]), int(pos[1])), 10, 10), newpos_skeleton)

    def on_render(self):
        """Render cam view and point joints."""
        self.sprites.clear(self.display_surf, self.background)
        self.display_surf.blit(self.frame, (0, 0))
        pygame.display.update()
        pygame.display.flip()

    def on_cleanup(self):
        """Bye bye."""
        pygame.quit()

    def on_execute(self):
        """Main loop of pygame."""
        self.on_init()
        while self._running:
            for event in pygame.event.get():
                self.on_event(event)
            self.on_loop()
            self.on_render()
        self.on_cleanup()


if __name__ == '__main__':
    game_app = Game()
    game_app.on_execute()
