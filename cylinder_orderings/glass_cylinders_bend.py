import mitsuba
import cv2 as cv
import math
import mpmath
import numpy as np

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
        'fov': 60,
        'to_world': T.look_at(origin=[math.cos(math.radians(phi)), 0.7, math.sin(math.radians(phi))], target=[0,0.2,0], up=[0, 0.05, 0]),
        'sampler': {
            'type': 'multijitter',
            'sample_count': 1024
        },
        'film': {
            'type': 'hdrfilm',
            'width': 512,
            'height': 512,
            'rfilter': {
                'type': 'tent',
            },
            'pixel_format': 'rgb',
        },
    })

def load_scene(filename, radiance):
    r = 0.05
    m = 10
    R = r*mpmath.csc(math.pi/m)
    print(R)
    #center = find_center_of_bounding_box()[0]
    #sizes = find_center_of_bounding_box()[1]
    #print(sizes)
    return mitsuba.load_dict({
        'type': 'scene',
        'id': 'my_scene',
        'integrator': {
            'type': 'path'
        },
        'bottom': {
            'type': 'cylinder',
            'radius': 0.23+r,
            'p0': [0,0,0],
            'p1': [0,0.01,0],
            'to_world': T.translate([0,0,0]),
            'bsdf': {
                'type': 'dielectric',
                'int_ior': 'bk7',
                'ext_ior': 'air'
            }
        },
        'glass': {
            'type': 'linearcurve',
            #'to_world': T.translate([0, 0.01, 0]).scale([0.05,0.05,0.05]),
            'filename': 'curves.txt',
            'bsdf': {
                'type': 'dielectric',
                'int_ior': 'bk7',
                'ext_ior': 'air'
            }
        },
        'floor': {
            'type': 'rectangle',
            #'to_world': T.translate([0,-0.05,0.05]).rotate([1,0,0],90).scale([0.3,0.3,0.3]),
            'to_world': T.translate([0,0,0.05]).rotate([1,0,0],-90),
            'bsdf': {
                'type': 'diffuse',
                'reflectance': {
                    'type': 'rgb',
                    'value': [0.1, 0.25, 0.3]
                }
            }
        },
        'sphere_1': {
            'type': 'rectangle',
            'to_world': T.translate([0,0,100]).rotate([1,0,0],-180).scale([100,100,100]),
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
                    'value': 5,
                }
            }
        }
    })

def find_center_of_bounding_box():
    scene = mitsuba.load_dict({
        'type': 'scene',
        'id': 'my_scene',
        'integrator': {
            'type': 'path'
        },
        'glass': {
            'type': 'obj',
            'filename': 'frames/frame20.obj',
            'bsdf': {
                'type': 'diffuse',
                'reflectance': {
                    'type': 'rgb',
                    'value': [0.2, 0.25, 0.7]
                }
            }
        },
        'light2': {
            'type': 'constant',
            'radiance': {
                'type': 'rgb',
                'value': 1
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
        sensor = load_sensor(0.001, phi, theta)
        mitsuba_image = mitsuba.render(scene, spp=1024, sensor=sensor)
        output_filename = f"views/view_{view_index:03d}.png"
        mitsuba.util.write_bitmap(output_filename, mitsuba_image)

    video=cv.VideoWriter('video.avi',cv.VideoWriter_fourcc(*'XVID'),50,(512,512))

    for i in range(0,num_views):
        video.write(cv.imread('views/view_'+ str("%03d"%i) +'.png'))

    video.release()

def main():
    scene = load_scene("test", 1)
    num_views = 360
    create_rotation_video(scene, num_views)

    video=cv.VideoWriter('video.avi',cv.VideoWriter_fourcc(*'XVID'),6,(512,512))

    for i in range(0,12):
        video.write(cv.imread('views/view_'+ str("%03d"%i) +'.png'))

    video.release()
    
    

if __name__ == "__main__":
    main()
