import mitsuba
import numpy as np
from variables import *
import config as cf
from colorama import Fore, Back, Style

import sys
import os

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from camera import *
from object import Object

if(config.use_gpu):
    mitsuba.set_variant("cuda_ad_rgb")
else:
    if(config.disable_cpu_parallelization == True):
        mitsuba.set_variant("scalar_rgb")
    else:
        mitsuba.set_variant("llvm_ad_rgb")

from matplotlib import pyplot as plt
from mitsuba import ScalarTransform4f as T

floor_scale_multiplier = 10
background_scale_multiplier = 2
background_distance_multiplier = 2

checkerboard_scale_vector = [1, 1, 0]
checkerboard_color0 = [0.02, 0.02, 0.02]  
checkerboard_color1 = [1.0, 1.0, 1.0] 

rectangle_light_scale_multiplier = 3
small_size_multiplier = 1/6
medium_size_multiplier = 1/3
large_size_multiplier = 1/2
small_distance_multiplier = 1
medium_distance_multiplier = 2
large_distance_multiplier = 3

class Scene:
    def __init__(self, objects = []):
        if len(objects)==0:
            self.objects = self.get_objects_from_json()
        else:
            self.objects = objects

        self.center, self.sizes = self.find_center_of_bounding_box()
        
        if config.target == "auto":
            target = self.center
        else:
            target = config.target

        if config.distance == "auto":
            distance = max(self.sizes)*2
        else:
            distance = config.distance

        self.camera = Camera(config.fov, distance, target, config.up_axis, config.width, config.height, config.samples_per_pixel, config.seed, config.rotation_axis, config.camera_axis)


        self.lights = self.get_lights_from_json()

        self.constant_radiance = 0

    def get_objects_from_json(self):
        objects = []
        objects_info = config.objects
        for object_info in objects_info:
            object = Object(object_info)
            objects.append(object)

        return objects
    
    def get_lights_from_json(self):
        lights = []

        light_obj : cf.LightConfig
        for light_obj in config.lights:
            if light_obj.emitter_type == "area":
                scale_vector, position, rotation = self.get_lights_position_info(light_obj)

                to_world = T.translate(position).scale(scale_vector) @ rotation
                light = {'type': light_obj.emitter_shape, 
                         'to_world':to_world, 
                         'bsdf': {
                            'type': 'diffuse',
                                'reflectance': {
                                    'type': 'rgb',
                                    'value': [1,1,1]
                                }
                         },
                         'emitter': {
                            'type': light_obj.emitter_type, 
                            'radiance': {
                                'type': 'rgb', 
                                'value': light_obj.emitter_radiance
                            },
                          }
                        }
            elif light_obj.emitter_type == "envmap":
                light = {'type': 'envmap',
                         'filename': light_obj.envmap_filename,
                         'to_world': T.rotate(light_obj.envmap_rotation_axis, light_obj.envmap_rotation_degrees),
                         'scale': light_obj.envmap_scale_factor
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
        elif(self.camera.up_axis == [-1,0,0]):
            rotation_axis = [0,1,0]
            rotation_angle = -90
            floor_center = [self.center[0]+self.sizes[0]/2, self.center[1], self.center[2]]
        elif(self.camera.up_axis == [0,0,1]):
            rotation_axis = [0,1,0]
            rotation_angle = 0
            floor_center = [self.center[0], self.center[1], self.center[2]-self.sizes[2]/2]
        elif(self.camera.up_axis == [0,0,-1]):
            rotation_axis = [0,1,0]
            rotation_angle = 180
            floor_center = [self.center[0], self.center[1], self.center[2]+self.sizes[2]/2]
        elif(self.camera.up_axis == [0,1,0]):
            rotation_axis = [1,0,0]
            rotation_angle = -90
            floor_center = [self.center[0], self.center[1]-self.sizes[1]/2, self.center[2]]
        elif(self.camera.up_axis == [0,-1,0]):
            rotation_axis = [1,0,0]
            rotation_angle = 90
            floor_center = [self.center[0], self.center[1]+self.sizes[1]/2, self.center[2]]

        return rotation_axis, rotation_angle, floor_center
    
    def get_background_position_info(self):
        #We must place the background according to the up_axis
        distance = [self.camera.depth_axis[0] * self.sizes[0]*background_distance_multiplier, self.camera.depth_axis[1] * self.sizes[1]*background_distance_multiplier, self.camera.depth_axis[2] * self.sizes[2]*background_distance_multiplier]
        background_center = self.center - distance

        if(self.camera.up_axis == [1,0,0] or self.camera.up_axis == [-1,0,0]):
            if(self.camera.depth_axis == [0,1,0]):
                rotation_axis = [1,0,0]
                rotation_angle = -90   
            elif(self.camera.depth_axis == [0,0,1]):
                rotation_axis = [1,0,0]
                rotation_angle = 0
            elif(self.camera.depth_axis == [0,-1,0]):
                rotation_axis = [1,0,0]
                rotation_angle = 90   
            elif(self.camera.depth_axis == [0,0,-1]):
                rotation_axis = [1,0,0]
                rotation_angle = 180

        elif(self.camera.up_axis == [0,0,1] or self.camera.up_axis == [0,0,-1]):
            if(self.camera.depth_axis == [0,1,0]):
                rotation_axis = [1,0,0]
                rotation_angle = -90   
            elif(self.camera.depth_axis == [1,0,0]):
                rotation_axis = [0,1,0]
                rotation_angle = 90
            elif(self.camera.depth_axis == [0,-1,0]):
                rotation_axis = [1,0,0]
                rotation_angle = 90   
            elif(self.camera.depth_axis == [-1,0,0]):
                rotation_axis = [0,1,0]
                rotation_angle = -90
            
        elif(self.camera.up_axis == [0,1,0] or self.camera.up_axis == [0,-1,0]):
            if(self.camera.depth_axis == [0,0,1]):
                rotation_axis = [0,1,0]
                rotation_angle = 0   
            elif(self.camera.depth_axis == [1,0,0]):
                rotation_axis = [0,1,0]
                rotation_angle = 90
            elif(self.camera.depth_axis == [0,0,-1]):
                rotation_axis = [0,1,0]
                rotation_angle = 180  
            elif(self.camera.depth_axis == [-1,0,0]):
                rotation_axis = [0,1,0]
                rotation_angle = -90

        return rotation_axis, rotation_angle, background_center
    
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
                'bsdf': object.material,
                'to_world': T.rotate(object.rotation_axis, object.rotation_degrees),
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

        bsdf_checkerboard = {
            "type": "diffuse",
            "reflectance": {
                "type": "checkerboard",
                "to_uv": T.scale(checkerboard_scale_vector),
                "color0": {
                    "type": "rgb",
                    "value": checkerboard_color0
                },
                "color1": {
                    "type": "rgb",
                    "value": checkerboard_color1
                }
            }
        }

        if(config.add_floor):
            rotation_axis, rotation_angle, floor_center = self.get_floor_position_info()
            
            floor = {
                'type': 'rectangle',
                'to_world': T.translate(floor_center).rotate(rotation_axis,rotation_angle).scale([max(self.sizes)*floor_scale_multiplier,max(self.sizes)*floor_scale_multiplier,max(self.sizes)*floor_scale_multiplier]),
            }

            if(config.floor_type == "checkerboard"):
                bsdf = bsdf_checkerboard
            else:
                bsdf = {
                    'type': config.floor_type,
                    'reflectance': {
                        'type': 'rgb',
                        'value': config.floor_color
                    }
                }
            
            floor['bsdf'] = bsdf
            my_scene['floor'] = floor

        if(config.add_background):
            rotation_axis, rotation_angle, floor_center = self.get_background_position_info()

            floor = {
                'type': 'rectangle',
                'to_world': T.translate(floor_center).rotate(rotation_axis,rotation_angle).scale([max(self.sizes)*background_scale_multiplier,max(self.sizes)*background_scale_multiplier,max(self.sizes)*background_scale_multiplier])
            }

            if(config.background_type == "checkerboard"):
                bsdf = bsdf_checkerboard
            else:
                bsdf = {
                    'type': config.background_type,
                    'reflectance': {
                        'type': 'rgb',
                        'value': config.background_color
                    }
                }
            
            
            floor['bsdf'] = bsdf
            my_scene['background'] = floor

        return mitsuba.load_dict(my_scene)
    
    
    
    def get_lights_position_info(self, light : cf.LightConfig):
        #Size of light
        scale_vector = [max(self.sizes),max(self.sizes),max(self.sizes)]
        if light.emitter_shape == "rectangle":
            scale_vector = [x*rectangle_light_scale_multiplier for x in scale_vector]
        
        if light.emitter_size == "small":
            scale_vector = [x*small_size_multiplier for x in scale_vector]
        elif light.emitter_size == "medium":
            scale_vector = [x*medium_size_multiplier for x in scale_vector]
        elif light.emitter_size == "large":
            scale_vector = [x*large_size_multiplier for x in scale_vector]
        else:
            scale_vector = light.emitter_size
        
        bottom_offset = np.array([self.sizes[0]/2-scale_vector[0], self.sizes[1]/2-scale_vector[1], self.sizes[2]/2-scale_vector[2]])

        #Distance of light from object
        distances = np.array([self.sizes[0], self.sizes[1], self.sizes[2]])
        
        if light.emitter_distance_from_object == "small":
            distances = [x*small_distance_multiplier for x in distances]
        elif light.emitter_distance_from_object == "medium":
            distances = [x*medium_distance_multiplier for x in distances]
        elif light.emitter_distance_from_object == "large":
            distances = [x*large_distance_multiplier for x in distances]
        else:
            distances = light.emitter_distance_from_object

        if(light.emitter_position != "bottom-center-back" and isinstance(light.emitter_position, str) and light.emitter_shape == "rectangle"):
            print(Fore.LIGHTYELLOW_EX + "Warning:" + light.emitter_position + " position not supported for rectangle, setting to bottom-center-back" + Style.RESET_ALL)
            light.emitter_position = "bottom-center-back"

        #Position of light
        if(light.emitter_position == "top-center"):
            position = np.array(self.center) + np.array(distances)* np.array(self.camera.up_axis)
        elif(light.emitter_position == "top-right"):
            position = np.array(self.center) + np.array(distances)* np.array(self.camera.up_axis) + np.array(distances) * np.array(self.camera.side_axis)
        elif(light.emitter_position == "top-left"):
            position = np.array(self.center) + np.array(distances)* np.array(self.camera.up_axis) - np.array(distances) * np.array(self.camera.side_axis)
        elif(light.emitter_position == "bottom-left"):
            position = np.array(self.center) - np.array(bottom_offset)* np.array(self.camera.up_axis) - np.array(distances) * np.array(self.camera.side_axis)
        elif(light.emitter_position == "bottom-right"):
            position = np.array(self.center) - np.array(bottom_offset)* np.array(self.camera.up_axis) + np.array(distances) * np.array(self.camera.side_axis)        
        elif(light.emitter_position == "top-center-front"):
            position = np.array(self.center) + np.array(distances)* np.array(self.camera.up_axis) + np.array(distances) * np.array(self.camera.depth_axis)
        elif(light.emitter_position == "top-left-front"):
            position = np.array(self.center) + np.array(distances)* np.array(self.camera.up_axis) - np.array(distances) * np.array(self.camera.side_axis) + np.array(distances) * np.array(self.camera.depth_axis)   
        elif(light.emitter_position == "top-right-front"):
            position = np.array(self.center) + np.array(distances)* np.array(self.camera.up_axis) + np.array(distances) * np.array(self.camera.side_axis) + np.array(distances) * np.array(self.camera.depth_axis)
        elif(light.emitter_position == "bottom-center-front"):
            position = np.array(self.center) - np.array(bottom_offset)* np.array(self.camera.up_axis) + np.array(distances) * np.array(self.camera.depth_axis)
        elif(light.emitter_position == "bottom-left-front"):
            position = np.array(self.center) - np.array(bottom_offset)* np.array(self.camera.up_axis) - np.array(distances) * np.array(self.camera.side_axis) + np.array(distances) * np.array(self.camera.depth_axis)
        elif(light.emitter_position == "bottom-right-front"):
            position = np.array(self.center) - np.array(bottom_offset)* np.array(self.camera.up_axis) + np.array(distances) * np.array(self.camera.side_axis) + np.array(distances) * np.array(self.camera.depth_axis)
        elif(light.emitter_position == "top-center-back"):
            position = np.array(self.center) + np.array(distances)* np.array(self.camera.up_axis) - np.array(distances) * np.array(self.camera.depth_axis)
        elif(light.emitter_position == "top-left-back"):
            position = np.array(self.center) + np.array(distances)* np.array(self.camera.up_axis) - np.array(distances) * np.array(self.camera.side_axis) - np.array(distances) * np.array(self.camera.depth_axis)
        elif(light.emitter_position == "top-right-back"):
            position = np.array(self.center) + np.array(distances)* np.array(self.camera.up_axis) + np.array(distances) * np.array(self.camera.side_axis) - np.array(distances) * np.array(self.camera.depth_axis)
        elif(light.emitter_position == "bottom-center-back"):
            position = np.array(self.center) - np.array(bottom_offset)* np.array(self.camera.up_axis) - np.array(distances) * np.array(self.camera.depth_axis)
        elif(light.emitter_position == "bottom-left-back"):
            position = np.array(self.center) - np.array(bottom_offset)* np.array(self.camera.up_axis) - np.array(distances) * np.array(self.camera.side_axis) - np.array(distances) * np.array(self.camera.depth_axis)
        elif(light.emitter_position == "bottom-right-back"):
            position = np.array(self.center) - np.array(bottom_offset)* np.array(self.camera.up_axis) + np.array(distances) * np.array(self.camera.side_axis) - np.array(distances) * np.array(self.camera.depth_axis)
        else:
            position = light.emitter_position
            rotation = T.rotate(light.emitter_rotation_axis, light.emitter_rotation_degrees)

        if(light.emitter_position == "bottom-center-back" or (light.emitter_shape == "rectangle" and isinstance(light.emitter_position,str))):
            position = np.array(self.center) - np.array(bottom_offset)* np.array(self.camera.up_axis) - np.array(distances) * np.array(self.camera.depth_axis)
            
            if(self.camera.up_axis == [1,0,0]):
                if(self.camera.depth_axis == [0,1,0]):
                    rotation = T.rotate(self.camera.up_axis, -90)
                elif(self.camera.depth_axis == [0,-1,0]):
                    rotation = T.rotate(self.camera.up_axis, 90)
            elif(self.camera.up_axis == [-1,0,0]):
                if(self.camera.depth_axis == [0,1,0]):
                    rotation = T.rotate(self.camera.up_axis, 90)
                elif(self.camera.depth_axis == [0,-1,0]):
                    rotation = T.rotate(self.camera.up_axis, -90)
            elif(self.camera.up_axis == [0,1,0]):
                if(self.camera.depth_axis == [1,0,0]):
                    rotation = T.rotate(self.camera.up_axis, 90)
                elif(self.camera.depth_axis == [-1,0,0]):
                    rotation = T.rotate(self.camera.up_axis, -90)
            elif(self.camera.up_axis == [0,-1,0]):
                if(self.camera.depth_axis == [1,0,0]):
                    rotation = T.rotate(self.camera.up_axis, -90)
                elif(self.camera.depth_axis == [-1,0,0]):
                    rotation = T.rotate(self.camera.up_axis, 90)
            elif(self.camera.up_axis == [0,0,1]):
                rotation = T.rotate(self.camera.side_axis, 90)
            
            if(self.camera.depth_axis == [0,0,1]):
                rotation = T.rotate(self.camera.side_axis, 0)
            elif(self.camera.depth_axis == [0,0,-1]):
                rotation = T.rotate(self.camera.side_axis, 180)
        
        #No point of rotating a sphere object
        if light.emitter_shape == "sphere":
            rotation = T.rotate([1,0,0], 0)
        
        return scale_vector, position, rotation

