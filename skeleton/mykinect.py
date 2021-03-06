#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import openni
import pygame
from PIL import Image
import numpy as np

POSE2USE = 'Psi'


class Kinect(object):

    def __init__(self, game):
        self.game = game
        self.ctx = openni.Context()
        self.ctx.init()

        self.user = openni.UserGenerator()
        self.user.create(self.ctx)

        self.depth_generator = openni.DepthGenerator()
        self.depth_generator.create(self.ctx)
        self.depth_generator.set_resolution_preset(openni.RES_VGA)
        self.depth_generator.fps = 30

        self.image_generator = openni.ImageGenerator()
        self.image_generator.create(self.ctx)
        self.image_generator.set_resolution_preset(openni.RES_VGA)
        self.depth_generator.alternative_view_point_cap.set_view_point(self.image_generator)

        self.skel_cap = self.user.skeleton_cap
        self.pose_cap = self.user.pose_detection_cap

        # Define Joins we want to track
        self.joints = ['SKEL_HEAD', 'SKEL_LEFT_FOOT', 'SKEL_RIGHT_SHOULDER',
                       'SKEL_LEFT_HAND', 'SKEL_NECK',
                       'SKEL_RIGHT_FOOT', 'SKEL_LEFT_HIP', 'SKEL_RIGHT_HAND',
                       'SKEL_TORSO', 'SKEL_LEFT_ELBOW', 'SKEL_LEFT_KNEE',
                       'SKEL_RIGHT_HIP', 'SKEL_LEFT_SHOULDER',
                       'SKEL_RIGHT_ELBOW', 'SKEL_RIGHT_KNEE']

    def new_user(self, src, id):
        print "1/4 User {} detected. Looking for pose..." .format(id)
        self.pose_cap.start_detection(POSE2USE, id)

    def pose_detected(self, src, pose, id):
        print "2/4 Pose {} on user {}. Requesting calibration..." .format(pose, id)
        self.pose_cap.stop_detection(id)
        self.skel_cap.request_calibration(id, True)

    def calibration_start(self, src, id):
        print "3/4 Calibration started for user {}." .format(id)

    def calibration_in_progress(self, src, id, status):
        pass

    def calibration_complete(self, src, id, status):
        if status == openni.CALIBRATION_STATUS_OK:
            print "4/4 User {} calibrated successfully! Starting to track." .format(id)
            self.skel_cap.start_tracking(id)
        else:
            print "ERR User {} failed to calibrate. Restarting process." .format(id)
            self.new_user(self.user, id)

    def lost_user(self, src, id):
        print "--- User {} lost." .format(id)

    def get_joints(self):
        for id in self.user.users:
            if self.skel_cap.is_tracking(id) and self.skel_cap.is_calibrated(id):
                joints = [self.skel_cap.get_joint_position(id, j)
                          for j in map(lambda a: getattr(openni, a), self.joints)]

                return self.depth_generator.to_projective([j.point for j in joints])
                
    def register(self):
        self.user.register_user_cb(self.new_user, self.lost_user)
        self.pose_cap.register_pose_detected_cb(self.pose_detected)
        self.skel_cap.register_c_start_cb(self.calibration_start)
        self.skel_cap.register_c_in_progress_cb(self.calibration_in_progress)
        self.skel_cap.register_c_complete_cb(self.calibration_complete)
        self.skel_cap.set_profile(openni.SKEL_PROFILE_ALL)

    def capture_rgb(self):
        rgb_frame = np.fromstring(self.image_generator.get_raw_image_map_bgr(),
                                  dtype=np.uint8).reshape(self.game.size[1],
                                                          self.game.size[0], 3)
        image = Image.fromarray(rgb_frame)
        b, g, r = image.split()
        image = Image.merge("RGB", (r, g, b))
        self.game.frame = pygame.image.frombuffer(
            image.tostring(), image.size, 'RGB')

    def update_sensor(self):
        self.ctx.wait_any_update_all()
        
