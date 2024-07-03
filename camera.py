import mitsuba
import numpy as np
import util
from variables import *

if(config.use_gpu):
    mitsuba.set_variant("cuda_ad_rgb")
else:
    mitsuba.set_variant("llvm_ad_rgb")

from mitsuba import ScalarTransform4f as T

class Camera:
    def __init__(self, fov, distance, camera_target, up_axis = np.array([0,1,0]), width = 512, height = 512, spp = 224, seed=0, rotation_axis = [0,0,0], camera_axis=np.array([0,0,1])):
        self.fov = fov
        self.up_axis = up_axis
        
        self.camera_target = np.array(camera_target)
        self.width = width
        self.height = height
        self.samples_per_pixel = spp
        self.seed = seed

        if(rotation_axis== [0,0,0]):
            self.rotation_axis = up_axis
        else:
            self.rotation_axis = rotation_axis

        self.depth_axis = camera_axis
        #free_axis = np.array(self.up_axis) + np.array(self.depth_axis)
        
        #self.side_axis = [1-abs(free_axis[0]),1-abs(free_axis[1]),1-abs(free_axis[2])]
        
        if(up_axis== [1,0,0]):
            if(self.depth_axis == [0,1,0]):
                self.side_axis = [0,0,1]
            if(self.depth_axis == [0,-1,0]):
                self.side_axis = [0,0,-1]
            if(self.depth_axis == [0,0,1]):
                self.side_axis = [0,-1,0]
            if(self.depth_axis == [0,0,-1]):
                self.side_axis = [0,1,0]

        if(up_axis== [-1,0,0]):
            if(self.depth_axis == [0,1,0]):
                self.side_axis = [0,0,-1]
            if(self.depth_axis == [0,-1,0]):
                self.side_axis = [0,0,1]
            if(self.depth_axis == [0,0,1]):
                self.side_axis = [0,1,0]
            if(self.depth_axis == [0,0,-1]):
                self.side_axis = [0,-1,0]

        if(up_axis== [0,1,0]):
            if(self.depth_axis == [1,0,0]):
                self.side_axis = [0,0,-1]
            if(self.depth_axis == [-1,0,0]):
                self.side_axis = [0,0,1]
            if(self.depth_axis == [0,0,1]):
                self.side_axis = [1,0,0]
            if(self.depth_axis == [0,0,-1]):
                self.side_axis = [-1,0,0]
            
        if(up_axis== [0,-1,0]):
            if(self.depth_axis == [1,0,0]):
                self.side_axis = [0,0,1]
            if(self.depth_axis == [-1,0,0]):
                self.side_axis = [0,0,-1]
            if(self.depth_axis == [0,0,1]):
                self.side_axis = [-1,0,0]
            if(self.depth_axis == [0,0,-1]):
                self.side_axis = [1,0,0]
        
        if(up_axis== [0,0,1]):
            if(self.depth_axis == [1,0,0]):
                self.side_axis = [0,1,0]
            if(self.depth_axis == [-1,0,0]):
                self.side_axis = [0,-1,0]
            if(self.depth_axis == [0,1,0]):
                self.side_axis = [-1,0,0]
            if(self.depth_axis == [0,-1,0]):
                self.side_axis = [1,0,0]

        if(up_axis== [0,0,-1]):
            if(self.depth_axis == [1,0,0]):
                self.side_axis = [0,-1,0]
            if(self.depth_axis == [-1,0,0]):
                self.side_axis = [0,1,0]
            if(self.depth_axis == [0,1,0]):
                self.side_axis = [1,0,0]
            if(self.depth_axis == [0,-1,0]):
                self.side_axis = [-1,0,0]
         
        #print(free_axis)
        #print(self.side_axis)

        self.origin = np.array([camera_target[0]+distance*self.depth_axis[0],camera_target[1]+distance*self.depth_axis[1],camera_target[2]+distance*self.depth_axis[2]])

    def rotate_camera_origin(self, angle):
        theta = np.radians(angle)

        translated_camera_origin = self.origin - self.camera_target

        R = np.empty([3, 3])
        if(self.rotation_axis == [0,0,1]):
            R = np.array([[np.cos(theta), -np.sin(theta), 0],
                           [np.sin(theta), np.cos(theta), 0],
                           [0, 0, 1]])
        elif(self.rotation_axis == [0,1,0]):
            R = np.array([[np.cos(theta), 0, np.sin(theta)],
                           [0, 1, 0],
                           [-np.sin(theta), 0, np.cos(theta)]])
        else:
            R = np.array([[1, 0, 0],
                          [0, np.cos(theta), -np.sin(theta)],
                          [0, np.sin(theta), np.cos(theta)]])
            
        rotated_camera_origin = R @ translated_camera_origin

        new_camera_origin = rotated_camera_origin + self.camera_target

        return new_camera_origin
    
    def load_sensor(self, angle=0):
        return mitsuba.load_dict({
            'type': 'perspective',
            'fov': self.fov,
            'to_world': T.look_at(origin=self.rotate_camera_origin(angle), target=self.camera_target, up=self.up_axis),
            'principal_point_offset_x': 0,  #normalized principal point, [0,0] -> center of image
            'principal_point_offset_y': 0,
            'sampler': {
                'type': 'multijitter',
                'sample_count': self.samples_per_pixel,
                'seed': self.seed
            },
            'film': {
                'type': 'hdrfilm',
                'width': self.width,
                'height': self.height,
                'rfilter': {
                    'type': 'tent',
                },
                'pixel_format': 'rgb',
            },
        })
