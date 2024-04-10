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

mitsuba.set_variant("cuda_ad_rgb")

from matplotlib import pyplot as plt
from mitsuba import ScalarTransform4f as T

class Scene:
    def __init__(self, config_file, objects = []):
        with open(config_file, 'r') as file:
            self.data = json.load(file)

        if len(objects)==0:
            self.objects = self.get_objects_from_json()
        else:
            self.objects = objects

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
        else:
            self.add_floor = True

        if('add_background' in output_json and output_json['add_background']==False):
            self.add_background = False
        else:
            self.add_background = True

        if('floor_type' in output_json and output_json['floor_type']=="checkerboard"):
            self.floor_type = "checkerboard"
        else:
            self.floor_type = "diffuse"

        if('floor_color' in output_json):
            self.floor_color = output_json['floor_color']
        else:
            self.floor_color = [0.1, 0.25, 0.3]

        self.constant_radiance = 0

    def get_objects_from_json(self):
        objects = []
        objects_json = self.data['objects']
        for object_json in objects_json:
            object = Object(object_json)
            objects.append(object)

        return objects
    
    def get_lights_from_json(self):
        lights = []
        lights_json = self.data['lights']

        for data in lights_json:
            if data['emitter_type'] == "area":
                scale_vector, position, rotation = self.get_lights_position_info(data)

                to_world = T.translate(position).scale(scale_vector) @ rotation
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
            elif data['emitter_type'] == "envmap":
                light = {'type': 'envmap',
                         'filename': data['filename'],
                         'to_world': T.rotate([1, 0, 0], 90),
                         'scale': 0.5
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
            #print(object.name)
            my_scene[object.name] = {'type': object.type, 'filename': object.filename}

        scene = mitsuba.load_dict(my_scene)    

        bbox = scene.bbox()

        center = (bbox.min + bbox.max) / 2

        size_x = bbox.max.x - bbox.min.x
        size_y = bbox.max.y - bbox.min.y
        size_z = bbox.max.z - bbox.min.z
        
        return center, [size_x, size_y, size_z]
    
    def get_floor_position_info(self):
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

        return rotation_axis, rotation_angle, floor_center
    
    def get_background_position_info(self):
        #We must place the background according to the up_axis
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

        return rotation_axis, rotation_angle, floor_center
    
    def load_scene(self):
        my_scene = {
            'type': 'scene',
            'id': 'my_scene',
            'integrator': {
                'type': 'path'
            }
        }

        for object in self.objects:
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

        if(self.add_floor):
            rotation_axis, rotation_angle, floor_center = self.get_floor_position_info()
            
            floor = {
                'type': 'rectangle',
                'to_world': T.translate(floor_center).rotate(rotation_axis,rotation_angle).scale([max(self.sizes)*10,max(self.sizes)*10,max(self.sizes)*10]),
            }

            if(self.floor_type == "checkerboard"):
                bsdf = {
                    'type': self.floor_type
                }
            else:
                bsdf = {
                    'type': self.floor_type,
                    'reflectance': {
                        'type': 'rgb',
                        'value': self.floor_color
                    }
                }
            
            floor['bsdf'] = bsdf
            my_scene['floor'] = floor

        if(self.add_background):
            rotation_axis, rotation_angle, floor_center = self.get_background_position_info()
            
            floor = {
                'type': 'rectangle',
                'to_world': T.translate(self.center-[0,10,0]).rotate([1,0,0],-90).scale([max(self.sizes)*10,max(self.sizes)*10,max(self.sizes)*10]),
            }

            bsdf = {
                "type": "diffuse",
                "reflectance": {
                    "type": "checkerboard",
                    "to_uv": T.scale([1, 1, 0]),
                    "color0": {
                        "type": "rgb",
                        "value": [0.02, 0.02, 0.02]  
                    },
                    "color1": {
                        "type": "rgb",
                        "value": [1.0, 1.0, 1.0] 
                    }
                }
            }
            
            
            floor['bsdf'] = bsdf
            my_scene['background'] = floor

        return mitsuba.load_dict(my_scene)
    
    
    
    def get_lights_position_info(self, data):
        #Size of light
        scale_vector = [max(self.sizes),max(self.sizes),max(self.sizes)]
        if data['emitter_shape'] == "rectangle":
            scale_vector = [x*3 for x in scale_vector]
        if 'size' in data:
            if data['size'] == "small":
                scale_vector = [x/6 for x in scale_vector]
            elif data['size'] == "medium":
                scale_vector = [x/3 for x in scale_vector]
            elif data['size'] == "large":
                scale_vector = [x/2 for x in scale_vector]
            else:
                scale_vector = data['size']
        else:
            scale_vector = [x/3 for x in scale_vector]
        
        bottom_offset = np.array([self.sizes[0]/2-scale_vector[0], self.sizes[1]/2-scale_vector[1], self.sizes[2]/2-scale_vector[2]])

        #Distance of light from object
        distances = np.array([self.sizes[0], self.sizes[1], self.sizes[2]])
        if 'distance_from_object' in data:
            if data['distance_from_object'] == "small":
                distances = distances
            elif data['distance_from_object'] == "medium":
                distances = [x*2 for x in distances]
            elif data['distance_from_object'] == "large":
                distances = [x*3 for x in distances]
            else:
                distances = data['distance_from_object']
        else:
            distances = [x*2 for x in distances]

        #Position of light
        if(data['position'] == "top-center"):
            position = np.array(self.center) + np.array(distances)* np.array(self.camera.up_axis)
            rotation = T.rotate(self.camera.side_axis, 180)
        elif(data['position'] == "top-right"):
            position = np.array(self.center) + np.array(distances)* np.array(self.camera.up_axis) - np.array(distances) * np.array(self.camera.side_axis)
            rotation = T.rotate(self.camera.side_axis, 180).rotate(self.camera.depth_axis, 45)
        elif(data['position'] == "top-left"):
            position = np.array(self.center) + np.array(distances)* np.array(self.camera.up_axis) + np.array(distances) * np.array(self.camera.side_axis)
            rotation = T.rotate(self.camera.side_axis, 180).rotate(self.camera.depth_axis, -45)
        elif(data['position'] == "bottom-left"):
            position = np.array(self.center) - np.array(bottom_offset)* np.array(self.camera.up_axis) + np.array(distances) * np.array(self.camera.side_axis)
            rotation = T.rotate(self.camera.side_axis, 90).rotate(self.camera.depth_axis, -90)
        elif(data['position'] == "bottom-right"):
            position = np.array(self.center) - np.array(bottom_offset)* np.array(self.camera.up_axis) - np.array(distances) * np.array(self.camera.side_axis)
            rotation = T.rotate(self.camera.side_axis, 90).rotate(self.camera.depth_axis, 90)
        elif(data['position'] == "top-center-front"):
            position = np.array(self.center) + np.array(distances)* np.array(self.camera.up_axis) + np.array(distances) * np.array(self.camera.depth_axis)
            rotation = T.rotate(self.camera.side_axis, -225)
        elif(data['position'] == "top-left-front"):
            position = np.array(self.center) + np.array(distances)* np.array(self.camera.up_axis) + np.array(distances) * np.array(self.camera.side_axis) + np.array(distances) * np.array(self.camera.depth_axis)
            rotation = T.rotate(self.camera.side_axis, 135).rotate(self.camera.depth_axis, 45)
        elif(data['position'] == "top-right-front"):
            position = np.array(self.center) + np.array(distances)* np.array(self.camera.up_axis) - np.array(distances) * np.array(self.camera.side_axis) + np.array(distances) * np.array(self.camera.depth_axis)
            rotation = T.rotate(self.camera.side_axis, 135).rotate(self.camera.depth_axis, -45)
        elif(data['position'] == "bottom-center-front"):
            position = np.array(self.center) - np.array(bottom_offset)* np.array(self.camera.up_axis) + np.array(distances) * np.array(self.camera.depth_axis)
            rotation = T.rotate(self.camera.side_axis, 90)
        elif(data['position'] == "bottom-left-front"):
            position = np.array(self.center) - np.array(bottom_offset)* np.array(self.camera.up_axis) + np.array(distances) * np.array(self.camera.side_axis) + np.array(distances) * np.array(self.camera.depth_axis)
            rotation = T.rotate(self.camera.side_axis, 90).rotate(self.camera.depth_axis, -45)
        elif(data['position'] == "bottom-right-front"):
            position = np.array(self.center) - np.array(bottom_offset)* np.array(self.camera.up_axis) - np.array(distances) * np.array(self.camera.side_axis) + np.array(distances) * np.array(self.camera.depth_axis)
            rotation = T.rotate(self.camera.side_axis, 90).rotate(self.camera.depth_axis, 45)
        elif(data['position'] == "top-center-back"):
            position = np.array(self.center) + np.array(distances)* np.array(self.camera.up_axis) - np.array(distances) * np.array(self.camera.depth_axis)
            rotation = T.rotate(self.camera.side_axis, -90).rotate(self.camera.side_axis, -45)
        elif(data['position'] == "top-left-back"):
            position = np.array(self.center) + np.array(distances)* np.array(self.camera.up_axis) + np.array(distances) * np.array(self.camera.side_axis) - np.array(distances) * np.array(self.camera.depth_axis)
            rotation = T.rotate(self.camera.side_axis, -90).rotate(self.camera.depth_axis, -45).rotate(self.camera.side_axis, -45)
        elif(data['position'] == "top-right-back"):
            position = np.array(self.center) + np.array(distances)* np.array(self.camera.up_axis) - np.array(distances) * np.array(self.camera.side_axis) - np.array(distances) * np.array(self.camera.depth_axis)
            rotation = T.rotate(self.camera.side_axis, -90).rotate(self.camera.depth_axis, 45).rotate(self.camera.side_axis, -45)
        elif(data['position'] == "bottom-center-back"):
            position = np.array(self.center) - np.array(bottom_offset)* np.array(self.camera.up_axis) - np.array(distances) * np.array(self.camera.depth_axis)
            rotation = T.rotate(self.camera.side_axis, -90)
        elif(data['position'] == "bottom-left-back"):
            position = np.array(self.center) - np.array(bottom_offset)* np.array(self.camera.up_axis) + np.array(distances) * np.array(self.camera.side_axis) - np.array(distances) * np.array(self.camera.depth_axis)
            rotation = T.rotate(self.camera.side_axis, -90).rotate(self.camera.depth_axis, -45)
        elif(data['position'] == "bottom-right-back"):
            position = np.array(self.center) - np.array(bottom_offset)* np.array(self.camera.up_axis) - np.array(distances) * np.array(self.camera.side_axis) - np.array(distances) * np.array(self.camera.depth_axis)
            rotation = T.rotate(self.camera.side_axis, -90).rotate(self.camera.depth_axis, 45)

        return scale_vector, position, rotation

