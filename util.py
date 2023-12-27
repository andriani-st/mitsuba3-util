import mitsuba
import open3d as o3d
import json
import cv2 as cv
import numpy as np
import math
import os
import time
import matplotlib.pyplot as plt
from object import Object

mitsuba.set_variant("scalar_rgb")

from matplotlib import pyplot as plt
from mitsuba import ScalarTransform4f as T

def load_sensor(r, phi, theta):
    # Apply two rotations to convert from spherical coordinates to world 3D coordinates.
    origin = T.rotate([0, 0, 1], phi).rotate([0, 1, 0], theta) @ mitsuba.ScalarPoint3f([0, 0, r])
    print("-----------------------------------")
    #print(origin)
    #print([0, math.sin(math.radians(phi)), math.cos(math.radians(phi))])
    return mitsuba.load_dict({
        'type': 'perspective',
        'fov': 20,
        'to_world': T.look_at(origin=[math.cos(math.radians(phi)), 0.4, math.sin(math.radians(phi))], target=[0,0,0], up=[0, r, 0]),
        'sampler': {
            'type': 'multijitter',
            'sample_count': 16
        },
        'film': {
            'type': 'hdrfilm',
            'width': 640,
            'height': 480,
            'rfilter': {
                'type': 'tent',
            },
            'pixel_format': 'rgb',
        },
    })

def load_scene(filename, radiance):

    center = find_center_of_bounding_box()[0]
    sizes = find_center_of_bounding_box()[1]
    print(sizes)
    return mitsuba.load_dict({
        'type': 'scene',
        'id': 'my_scene',
        'integrator': {
            'type': 'path'
        },
        'glass': {
            'type': 'obj',
            'filename': filename,
            'to_world': T.rotate([0,1,0],70).translate(-center),
            #'bsdf': {
            #    'type': 'diffuse',
            #    'reflectance': {
            #        'type': 'rgb',
            #        'value': [0.8, 0.25, 0.3]
            #    }
            #}
            'bsdf': {
                'type': 'dielectric',
                #'distribution': 'beckmann',
                #'alpha': 0.1,
                'int_ior': 'bk7',
                'ext_ior': 'air'
            }
        },
        'sphere_1': {
            'type': 'sphere',
            'center': [-sizes[0], -sizes[1]/2+0.03, sizes[2]],
            'radius': 0.03,
            'bsdf': {
                'type': 'diffuse',
                'reflectance': {
                    'type': 'rgb',
                    'value': [1, 0, 0]
                }
            },
            'emitter': {
                'type': 'area',
                'radiance': {
                    'type': 'rgb',
                    'value': radiance,
                }
            }
        },
        'sphere_2': {
            'type': 'sphere',
            'center': [sizes[0], -sizes[1]/2+0.03, sizes[2]],
            'radius': 0.03,
            'bsdf': {
                'type': 'diffuse',
                'reflectance': {
                    'type': 'rgb',
                    'value': [1, 0, 0]
                }
            },
            'emitter': {
                'type': 'area',
                'radiance': {
                    'type': 'rgb',
                    'value': radiance,
                }
            }
        },
        'floor': {
            'type': 'rectangle',
            'to_world': T.translate([0,-0.05,0.05]).rotate([1,0,0],-90),
            'bsdf': {
                'type': 'diffuse',
                'reflectance': {
                    'type': 'rgb',
                    'value': [0.1, 0.25, 0.3]
                }
            }
        },
        #'light2': {
        #    'type': 'constant',
        #    'radiance': {
        #       'type': 'rgb',
        #        'value': 1,
        #    }
        #}
    })

def find_center_of_bounding_box():
    scene = mitsuba.load_dict({
        'type': 'scene',
        'id': 'my_scene',
        'integrator': {
            'type': 'path'
        },
        'object': {
            'type': 'obj',
            'filename': 'frames/frame20.obj',
            'bsdf': {
                'type': 'diffuse',
                'reflectance': {
                    'type': 'rgb',
                    'value': [0.2, 0.25, 0.7]
                }
            }
        }
    })

    bbox = scene.bbox()

    center = (bbox.min + bbox.max) / 2

    size_x = bbox.max.x - bbox.min.x
    size_y = bbox.max.y - bbox.min.y
    size_z = bbox.max.z - bbox.min.z

    return center, [size_x, size_y, size_z]

def create_rotation_video(scene, num_views):
    for view_index in range(num_views):
        phi = 360.0 / num_views * view_index  # Calculate the azimuthal angle
        theta = 160.0  # You can set the polar angle to a fixed value or vary it as well
        sensor = load_sensor(5, phi, theta)
        mitsuba_image = mitsuba.render(scene, spp=16, sensor=sensor)
        output_filename = f"views/view_{view_index:03d}.png"
        mitsuba.util.write_bitmap(output_filename, mitsuba_image)

    video=cv.VideoWriter('video.avi',cv.VideoWriter_fourcc(*'XVID'),10,(400,400))

    for i in range(0,num_views):
        video.write(cv.imread('views/view_'+ str("%03d"%i) +'.png'))

    video.release()

def create_animation_video_fixed_angle():
    sensor = load_sensor(5, 270, 160)

    for i in range(1,21):
        scene = load_scene('frames/frame' + str(i) + '.obj', 20)
        image = mitsuba.render(scene, spp=1024, sensor=sensor)
        mitsuba.util.write_bitmap('result/result' + str(i) + '.png', image)

    video=cv.VideoWriter('video.avi',cv.VideoWriter_fourcc(*'XVID'),10,(1920,1080))
    for i in range(1,21):
        video.write(cv.imread('result/result' + str(i) + '.png'))

    video.release()

def create_animation_rotation_video(num_views):
    frame = 1
    for view_index in range(num_views):
        phi = 360.0 / num_views * view_index  # Calculate the azimuthal angle
        theta = 160.0  # You can set the polar angle to a fixed value or vary it as well
        sensor = load_sensor(5, phi, theta)

        scene = load_scene('frames/frame' + str(frame) + '.obj', 20)
        frame += 1

        image = mitsuba.render(scene, spp=1024, sensor=sensor)
        mitsuba.util.write_bitmap('result/result' + str(view_index) + '.png', image)

        if frame > 20:
            frame = 1
    
    video=cv.VideoWriter('video.avi',cv.VideoWriter_fourcc(*'XVID'),10,(640,480))
    for i in range(0,360):
        video.write(cv.imread('result/result' + str(i) + '.png'))

    video.release()

def jsonReader():
  f = open('config.json')
  data = json.load(f)
  
  objects = []
  for obj_data in data['objects']:
    obj = Object(obj_data) 
    objects.append(obj)

  for obj in objects:
    print(obj.name)


def main():
    #test_scene()
    #create_animation_video_fixed_angle()
    
    #num_views = 360
    #create_rotation_video(scene, num_views)
    #create_animation_rotation_video(num_views)
    jsonReader()
    
    

if __name__ == "__main__":
    main()