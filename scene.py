import mitsuba
import numpy as np
import math
import json

import sys
import os

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from camera import Camera
from object import Object

mitsuba.set_variant("scalar_rgb")

from matplotlib import pyplot as plt
from mitsuba import ScalarTransform4f as T

class Scene:
    def __init__(self, config_file):
        with open(config_file, 'r') as file:
            self.data = json.load(file)

        self.objects = self.get_objects_from_json()

        self.center, self.sizes = self.find_center_of_bounding_box()

        output_json = self.data['output']

        if(not 'target' in output_json or output_json['target']=="auto"):
            target = self.center
        else:
            target = output_json['target']

        if 'distance' in output_json:
            distance = output_json['distance']
        else:
            multiplier = 1
            if 'target' in output_json:
                if(output_json['distance_from_target_sign'] == "-"):
                    multiplier = -1
            
            distance = max(self.sizes)*2*multiplier

        self.camera = Camera(output_json['fov'], distance, target, output_json['up_axis'], output_json['width'], output_json['height'], output_json['samples_per_pixel'], output_json['rotation_axis'])


        self.lights = self.get_lights_from_json()
        if('add_floor' in output_json and output_json['add_floor']==False):
            self.add_floor = False

        self.constant_radiance = 0

    def get_objects_from_json(self):
        objects = []
        objects_json = self.data['objects']
        for object_json in objects_json:
            object = Object(object_json)
            objects.append(object)
            print(object_json)

        return objects
    
    def get_lights_from_json(self):
        lights = []
        lights_json = self.data['lights']

        position_top_center = [self.center[0]+self.sizes[0]*self.camera.up_axis[0], self.center[1]+self.sizes[1]*self.camera.up_axis[1], self.center[2]+self.sizes[2]*self.camera.up_axis[2]]
        position_top_left = [self.center[0]+self.sizes[0]*self.camera.up_axis[0]+self.sizes[0]*self.camera.side_axis[0], self.center[1]+self.sizes[1]*self.camera.up_axis[1]+self.sizes[1]*self.camera.side_axis[1], self.center[2]+self.sizes[2]*self.camera.up_axis[2]+self.sizes[2]*self.camera.side_axis[2]]
        position_top_right = [self.center[0]+self.sizes[0]*self.camera.up_axis[0]-self.sizes[0]*self.camera.side_axis[0], self.center[1]+self.sizes[1]*self.camera.up_axis[1]-self.sizes[1]*self.camera.side_axis[1], self.center[2]+self.sizes[2]*self.camera.up_axis[2]-self.sizes[2]*self.camera.side_axis[2]]

        position_bottom_left = [self.center[0]-self.sizes[0]/2*self.camera.up_axis[0]+max(self.sizes)/5*self.camera.up_axis[0]+self.sizes[0]*self.camera.side_axis[0], self.center[1]-self.sizes[1]/2*self.camera.up_axis[1]+max(self.sizes)/5*self.camera.up_axis[1]+self.sizes[1]*self.camera.side_axis[1], self.center[2]-self.sizes[2]/2*self.camera.up_axis[2]+max(self.sizes)/5*self.camera.up_axis[2]+self.sizes[2]*self.camera.side_axis[2]]
        position_bottom_right = [self.center[0]-self.sizes[0]/2*self.camera.up_axis[0]+max(self.sizes)/5*self.camera.up_axis[0]-self.sizes[0]*self.camera.side_axis[0], self.center[1]-self.sizes[1]/2*self.camera.up_axis[1]+max(self.sizes)/5*self.camera.up_axis[1]-self.sizes[1]*self.camera.side_axis[1], self.center[2]-self.sizes[2]/2*self.camera.up_axis[2]+max(self.sizes)/5*self.camera.up_axis[2]-self.sizes[2]*self.camera.side_axis[2]]
        
        position_top_center_front = [self.center[0]+self.sizes[0]*self.camera.up_axis[0]+self.sizes[0]*self.camera.depth_axis[0], self.center[1]+self.sizes[1]*self.camera.up_axis[1]+self.sizes[1]*self.camera.depth_axis[1], self.center[2]+self.sizes[2]*self.camera.up_axis[2]+self.sizes[0]*self.camera.depth_axis[2]]
        position_top_left_front = [self.center[0]+self.sizes[0]*self.camera.up_axis[0]+self.sizes[0]*self.camera.side_axis[0]+self.sizes[0]*self.camera.depth_axis[0], self.center[1]+self.sizes[1]*self.camera.up_axis[1]+self.sizes[1]*self.camera.side_axis[1]+self.sizes[1]*self.camera.depth_axis[1], self.center[2]+self.sizes[2]*self.camera.up_axis[2]+self.sizes[2]*self.camera.side_axis[2]+self.sizes[0]*self.camera.depth_axis[2]]
        position_top_right_front = [self.center[0]+self.sizes[0]*self.camera.up_axis[0]-self.sizes[0]*self.camera.side_axis[0]+self.sizes[0]*self.camera.depth_axis[0], self.center[1]+self.sizes[1]*self.camera.up_axis[1]-self.sizes[1]*self.camera.side_axis[1]+self.sizes[1]*self.camera.depth_axis[1], self.center[2]+self.sizes[2]*self.camera.up_axis[2]-self.sizes[2]*self.camera.side_axis[2]+self.sizes[2]*self.camera.depth_axis[2]]

        position_bottom_center_front = [self.center[0]-self.sizes[0]/2*self.camera.up_axis[0]+max(self.sizes)/5*self.camera.up_axis[0]+self.sizes[0]*self.camera.depth_axis[0], self.center[1]-self.sizes[1]/2*self.camera.up_axis[1]+max(self.sizes)/5*self.camera.up_axis[1]+self.sizes[1]*self.camera.depth_axis[1], self.center[2]-self.sizes[2]/2*self.camera.up_axis[2]+max(self.sizes)/5*self.camera.up_axis[2]+self.sizes[0]*self.camera.depth_axis[2]]
        position_bottom_left_front = [self.center[0]-self.sizes[0]/2*self.camera.up_axis[0]+max(self.sizes)/5*self.camera.up_axis[0]+self.sizes[0]*self.camera.side_axis[0]+self.sizes[0]*self.camera.depth_axis[0], self.center[1]-self.sizes[1]/2*self.camera.up_axis[1]+max(self.sizes)/5*self.camera.up_axis[1]+self.sizes[1]*self.camera.side_axis[1]+self.sizes[1]*self.camera.depth_axis[1], self.center[2]-self.sizes[2]/2*self.camera.up_axis[2]+max(self.sizes)/5*self.camera.up_axis[2]+self.sizes[2]*self.camera.side_axis[2]+self.sizes[0]*self.camera.depth_axis[2]]
        position_bottom_right_front = [self.center[0]-self.sizes[0]/2*self.camera.up_axis[0]+max(self.sizes)/5*self.camera.up_axis[0]-self.sizes[0]*self.camera.side_axis[0]+self.sizes[0]*self.camera.depth_axis[0], self.center[1]-self.sizes[1]/2*self.camera.up_axis[1]+max(self.sizes)/5*self.camera.up_axis[1]-self.sizes[1]*self.camera.side_axis[1]+self.sizes[1]*self.camera.depth_axis[1], self.center[2]-self.sizes[2]/2*self.camera.up_axis[2]+max(self.sizes)/5*self.camera.up_axis[2]-self.sizes[2]*self.camera.side_axis[2]+self.sizes[2]*self.camera.depth_axis[2]]
        
        position_top_center_back = [self.center[0]+self.sizes[0]*self.camera.up_axis[0]-self.sizes[0]*self.camera.depth_axis[0], self.center[1]+self.sizes[1]*self.camera.up_axis[1]+self.sizes[1]*self.camera.depth_axis[1], self.center[2]+self.sizes[2]*self.camera.up_axis[2]-self.sizes[0]*self.camera.depth_axis[2]]
        position_top_left_back = [self.center[0]+self.sizes[0]*self.camera.up_axis[0]+self.sizes[0]*self.camera.side_axis[0]-self.sizes[0]*self.camera.depth_axis[0], self.center[1]+self.sizes[1]*self.camera.up_axis[1]+self.sizes[1]*self.camera.side_axis[1]-self.sizes[1]*self.camera.depth_axis[1], self.center[2]+self.sizes[2]*self.camera.up_axis[2]+self.sizes[2]*self.camera.side_axis[2]-self.sizes[0]*self.camera.depth_axis[2]]
        position_top_right_back = [self.center[0]+self.sizes[0]*self.camera.up_axis[0]-self.sizes[0]*self.camera.side_axis[0]-self.sizes[0]*self.camera.depth_axis[0], self.center[1]+self.sizes[1]*self.camera.up_axis[1]-self.sizes[1]*self.camera.side_axis[1]-self.sizes[1]*self.camera.depth_axis[1], self.center[2]+self.sizes[2]*self.camera.up_axis[2]-self.sizes[2]*self.camera.side_axis[2]-self.sizes[2]*self.camera.depth_axis[2]]

        position_bottom_center_back = [self.center[0]-self.sizes[0]/2*self.camera.up_axis[0]+max(self.sizes)/5*self.camera.up_axis[0]-self.sizes[0]*self.camera.depth_axis[0], self.center[1]-self.sizes[1]/2*self.camera.up_axis[1]+max(self.sizes)/5*self.camera.up_axis[1]-self.sizes[1]*self.camera.depth_axis[1], self.center[2]-self.sizes[2]/2*self.camera.up_axis[2]+max(self.sizes)/5*self.camera.up_axis[2]-self.sizes[0]*self.camera.depth_axis[2]]
        position_bottom_left_back = [self.center[0]-self.sizes[0]/2*self.camera.up_axis[0]+max(self.sizes)/5*self.camera.up_axis[0]+self.sizes[0]*self.camera.side_axis[0]-self.sizes[0]*self.camera.depth_axis[0], self.center[1]-self.sizes[1]/2*self.camera.up_axis[1]+max(self.sizes)/5*self.camera.up_axis[1]+self.sizes[1]*self.camera.side_axis[1]-self.sizes[1]*self.camera.depth_axis[1], self.center[2]-self.sizes[2]/2*self.camera.up_axis[2]+max(self.sizes)/5*self.camera.up_axis[2]+self.sizes[2]*self.camera.side_axis[2]-self.sizes[0]*self.camera.depth_axis[2]]
        position_bottom_right_back = [self.center[0]-self.sizes[0]/2*self.camera.up_axis[0]+max(self.sizes)/5*self.camera.up_axis[0]-self.sizes[0]*self.camera.side_axis[0]-self.sizes[0]*self.camera.depth_axis[0], self.center[1]-self.sizes[1]/2*self.camera.up_axis[1]+max(self.sizes)/5*self.camera.up_axis[1]-self.sizes[1]*self.camera.side_axis[1]-self.sizes[1]*self.camera.depth_axis[1], self.center[2]-self.sizes[2]/2*self.camera.up_axis[2]+max(self.sizes)/5*self.camera.up_axis[2]-self.sizes[2]*self.camera.side_axis[2]-self.sizes[2]*self.camera.depth_axis[2]]
        
        for data in lights_json:
            if data['emitter_type'] == "area":
                if(data['position'] == "top-center"):
                    position = position_top_center
                elif(data['position'] == "top-right"):
                    position = position_top_right
                elif(data['position'] == "top-left"):
                    position = position_top_left
                elif(data['position'] == "bottom-left"):
                    position = position_bottom_left
                elif(data['position'] == "bottom-right"):
                    position = position_bottom_right
                elif(data['position'] == "top-center-front"):
                    position = position_top_center_front
                elif(data['position'] == "top-left-front"):
                    position = position_top_left_front
                elif(data['position'] == "top-right-front"):
                    position = position_top_right_front
                elif(data['position'] == "bottom-center-front"):
                    position = position_bottom_center_front
                elif(data['position'] == "bottom-left-front"):
                    position = position_bottom_left_front
                elif(data['position'] == "bottom-right-front"):
                    position = position_bottom_right_front
                elif(data['position'] == "top-center-back"):
                    position = position_top_center_back
                elif(data['position'] == "top-left-back"):
                    position = position_top_left_back
                elif(data['position'] == "top-right-back"):
                    position = position_top_right_back
                elif(data['position'] == "bottom-center-back"):
                    position = position_bottom_center_back
                elif(data['position'] == "bottom-left-back"):
                    position = position_bottom_left_back
                elif(data['position'] == "bottom-right-back"):
                    position = position_bottom_right_back
            
                to_world = T.translate(position).scale([max(self.sizes)/5,max(self.sizes)/5,max(self.sizes)/5])
                light = {'type': data['emitter_shape'], 
                         'to_world':to_world, 
                         'bsdf': {
                            'type': 'diffuse',
                                'reflectance': {
                                    'type': 'rgb',
                                    'value': [1,1,1]
                                }
                         },
                         'emitter': {
                            'type': data['emitter_type'], 
                            'radiance': {
                                'type': 'rgb', 
                                'value': data['radiance']
                            },
                          }
                        }
            lights.append(light)

        return lights

    def find_center_of_bounding_box(self):
        my_scene = {
            'type': 'scene',
            'id': 'my_scene',
            'integrator': {
                'type': 'path'
            }
        }

        for object in self.objects:
            print(object.name)
            my_scene[object.name] = {'type': object.type, 'filename': object.filename}

        scene = mitsuba.load_dict(my_scene)    

        bbox = scene.bbox()

        center = (bbox.min + bbox.max) / 2

        size_x = bbox.max.x - bbox.min.x
        size_y = bbox.max.y - bbox.min.y
        size_z = bbox.max.z - bbox.min.z
        
        return center, [size_x, size_y, size_z]
    
    def load_scene(self, add_floor=True):
        my_scene = {
            'type': 'scene',
            'id': 'my_scene',
            'integrator': {
                'type': 'path'
            }
        }

        for object in self.objects:
            print(object.name)
            object_dict = {
                'type': object.type,
                'filename': object.filename,
                'bsdf': object.material
            }
            my_scene[object.name] = object_dict

        light_index=0
        for light in self.lights:
            light_index += 1
            my_scene['light'+str(light_index)] = light

        if(self.constant_radiance != 0):
            constant_lighting = {
                'type': 'constant',
                'radiance': {
                    'type': 'rgb',
                    'value': self.constant_radiance
                } 
            }
            my_scene['constant_lighting'] = constant_lighting

        if(add_floor):
            #We must place the floor according to the up_axis
            if(self.camera.up_axis == [1,0,0]):
                rotation_axis = [0,1,0]
                rotation_angle = 90
                floor_center = [self.center[0]-self.sizes[0]/2, self.center[1], self.center[2]]
            elif(self.camera.up_axis == [0,0,1]):
                rotation_axis = [0,1,0]
                rotation_angle = 0
                floor_center = [self.center[0], self.center[1], self.center[2]-self.sizes[2]/2]
            elif(self.camera.up_axis == [0,1,0]):
                rotation_axis = [1,0,0]
                rotation_angle = -90
                floor_center = [self.center[0], self.center[1]-self.sizes[1]/2, self.center[2]]
            
            floor = {
                'type': 'rectangle',
                'to_world': T.translate(floor_center).rotate(rotation_axis,rotation_angle).scale([max(self.sizes)*4,max(self.sizes)*4,max(self.sizes)*4]),
                'bsdf': {
                    'type': 'diffuse',
                    'reflectance': {
                        'type': 'rgb',
                        'value': [0.1, 0.25, 0.3]
                    }
                }
            }
            my_scene['floor'] = floor

        return mitsuba.load_dict(my_scene)
