import mitsuba
import numpy as np
import math

import sys
import os

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from camera import Camera
from scene import Scene

mitsuba.set_variant("scalar_rgb")

from matplotlib import pyplot as plt
from mitsuba import ScalarTransform4f as T

filigree_path = "/home/andriani/Documents/Master_thesis/mitsuba3-util/filigree/cylinder.obj"

def find_center_of_bounding_box():

    my_scene = {
        'type': 'scene',
        'id': 'my_scene',
        'integrator': {
            'type': 'path'
        },
        'skeleton': {
            'type': 'obj',
            'filename': filigree_path,
            #'to_world': T.rotate([1,0,0],180),
        }
    }

    scene = mitsuba.load_dict(my_scene)    

    bbox = scene.bbox()

    center = (bbox.min + bbox.max) / 2

    size_x = bbox.max.x - bbox.min.x
    size_y = bbox.max.y - bbox.min.y
    size_z = bbox.max.z - bbox.min.z

    return center, [size_x, size_y, size_z]

center, sizes = find_center_of_bounding_box()
print(center)
print(sizes)
camera = Camera(45, max(sizes)*2, center, [0,0,1], 512, 512, 224)

def load_scene(light_radiance=1, constant_radiance=0, add_floor = True, add_object=True):

    center, sizes = find_center_of_bounding_box()

    my_scene = {
        'type': 'scene',
        'id': 'my_scene',
        'integrator': {
            'type': 'path'
        },
        'light1': {
            'type': 'sphere',
            'to_world': T.translate([center[0]-sizes[0]/2,center[1]+sizes[1],center[2]+sizes[2]*2]).scale([3,3,3]),
            "bsdf": {
                "type": "diffuse",
                "reflectance": {
                    "type": "rgb",
                    "value": [1,1,1]
                }
            },
            'emitter': {
                'type': 'area',
                'radiance': {
                    'type': 'rgb',
                    'value': light_radiance,
                }
            }
        },
    }

    if(add_object):

        object = {
            'type': 'obj',
            'filename': filigree_path,
            #'to_world': T.rotate([1,0,0],-180),
            'bsdf': {
                'type': 'diffuse',
                #'material': 'Al',
                #'distribution': 'ggx',
                #'alpha_u': 0.1,
                #'alpha_v': 0.1
                #'reflectance': {
                #    'type': 'rgb',
                #    'value': [0.2, 0.2, 0.2]
                #}
            },
        }
        my_scene['skeleton'] = object

    if(constant_radiance != 0):
        constant_lighting = {
            'type': 'constant',
            'radiance': {
                'type': 'rgb',
                'value': constant_radiance
            } 
        }
        my_scene['constant_lighting'] = constant_lighting

    if(add_floor):
        #We must place the floor according to the up_axis
        if(camera.up_axis == [1,0,0]):
            rotation_axis = [0,1,0]
            rotation_angle = 90
            floor_center = [center[0]-sizes[0]/2, center[1], center[2]]
        elif(camera.up_axis == [0,0,1]):
            rotation_axis = [0,1,0]
            rotation_angle = 0
            floor_center = [center[0], center[1], center[2]-sizes[2]/2]
        elif(camera.up_axis == [0,1,0]):
            rotation_axis = [1,0,0]
            rotation_angle = -90
            floor_center = [center[0], center[1]-sizes[1]/2, center[2]]
        
        floor = {
            'type': 'rectangle',
            'to_world': T.translate(floor_center).rotate(rotation_axis,rotation_angle).scale([2000,2000,2000]),
            'bsdf': {
                'type': 'diffuse',
                'reflectance': {
                    'type': 'rgb',
                    'value': [0.1, 0.25, 0.3]
                }
            }
        }
        my_scene['floor'] = floor

    mesh_params = mitsuba.traverse(mitsuba.load_dict(my_scene))
    print(mesh_params)

    return mitsuba.load_dict(my_scene)

def main():
    #center, sizes = find_center_of_bounding_box()
    #camera = Camera(45, -max(sizes)*2, center, [0,1,0], 512, 512, 224, [1,0,0])

    #sensor = camera.load_sensor(0)

    #scene = load_scene(light_radiance=100, constant_radiance=0, add_floor=True, add_object=True)
    #image = mitsuba.render(scene, spp=camera.samples_per_pixel, sensor=sensor)
    #mitsuba.util.write_bitmap("result" + ".png", image)

    scene = Scene("../config.json")

    image = mitsuba.render(scene.load_scene(), spp=scene.camera.samples_per_pixel, sensor=scene.camera.load_sensor(0))

    mitsuba.util.write_bitmap("result" + ".png", image)
    
    
if __name__ == "__main__":
    main()