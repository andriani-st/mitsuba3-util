import mitsuba
import numpy as np
import math

mitsuba.set_variant("scalar_rgb")

from matplotlib import pyplot as plt
from mitsuba import ScalarTransform4f as T

tiles_path = "/home/andriani/Documents/Master_thesis/vitro/refactored/tiles/"
skeleton_path = "/home/andriani/Documents/Master_thesis/vitro/refactored/skeleton.obj"
colors_path = "/home/andriani/Documents/Master_thesis/vitro/refactored/colors.txt"

colors = []
with open(colors_path, 'r') as file:
    for line in file:
        color_components = [float(component)/255 for component in line.split()]
        colors.append(color_components)

print(colors[0])
n=len(colors)+1

def load_sensor(fov):
    center, sizes = find_center_of_bounding_box()

    return mitsuba.load_dict({
        'type': 'perspective',
        'fov': 45,
        'to_world': T.look_at(origin=[center[0],center[1],center[2]-max(sizes)-600], target=center, up=[0, 1, 0]),
        'principal_point_offset_x': 0,  #normalized principal point, [0,0] -> center of image
        'principal_point_offset_y': 0,
        'sampler': {
            'type': 'multijitter',
            'sample_count': 16
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

def load_scene(light_radiance=1, constant_radiance=0, add_floor = True, add_object=True):

    center, sizes = find_center_of_bounding_box()

    my_scene = {
        'type': 'scene',
        'id': 'my_scene',
        'integrator': {
            'type': 'path'
        },
        'background': {
            'type': 'rectangle',
            'to_world': T.translate([center[0],center[1],center[2]+200]).rotate([1,0,0],-180).scale([math.ceil(sizes[0])*2,math.ceil(sizes[1])*4,math.ceil(sizes[2])*2]),
            "bsdf": {
                "type": "diffuse",
                "reflectance": {
                    "type": "checkerboard",
                    "to_uv": T.scale([100, 0.5, 0]),
                    "color0": {
                        "type": "rgb",
                        "value": [0.2, 0.2, 0.2]  
                    },
                    "color1": {
                        "type": "rgb",
                        "value": [1.0, 1.0, 1.0] 
                    }
                }
            }
        },
        'light1': {
            'type': 'sphere',
            'to_world': T.translate([center[0]-sizes[0]/2,center[1]+sizes[1],center[2]+10]).scale([100,100,100]),
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
    '''
    'light2': {
        'type': 'sphere',
        'to_world': T.translate([center[0]+sizes[0]/2,center[1]+sizes[1],center[2]+10]).scale([100,100,100]),
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
    
    'light3': {
        'type': 'sphere',
        'to_world': T.translate([center[0]-sizes[0],center[1]-sizes[1]/2,center[2]+10]).scale([100,100,100]),
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
    }
    '''

    if(add_object):
        for i in range(1,n):
            object = {
                'type': 'obj',
                'filename': tiles_path+str(i).zfill(3)+'.obj',
                'to_world': T.rotate([1,0,0],-180),
                'bsdf': {
                    'type': 'dielectric',
                    'int_ior': 'bk7',
                    'ext_ior': 'air',
                    'specular_transmittance': {
                        'type': 'rgb',
                        'value': colors[i-1]
                },
                },
            }
            my_scene['object'+str(i)] = object

        object = {
            'type': 'obj',
            'filename': skeleton_path,
            'to_world': T.rotate([1,0,0],-180),
            'bsdf': {
                'type': 'conductor',
                'material': 'Al',
                #'distribution': 'ggx',
                #'alpha_u': 0.3,
                #'alpha_v': 0.5,
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
        floor = {
            'type': 'rectangle',
            'to_world': T.translate([center[0],center[1]-sizes[1]/2,center[2]]).rotate([1,0,0],-90).scale([2000,2000,2000]),
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


def find_center_of_bounding_box():

    my_scene = {
        'type': 'scene',
        'id': 'my_scene',
        'integrator': {
            'type': 'path'
        },
        'skeleton': {
            'type': 'obj',
            'filename': skeleton_path,
            'to_world': T.rotate([1,0,0],180),
        }
    }

    for i in range(1,n):
        object = {
            'type': 'obj',
            'filename': tiles_path+str(i).zfill(3)+'.obj',
            'to_world': T.rotate([1,0,0],-180),
            'bsdf': {
                'type': 'dielectric',
                'int_ior': 'bk7',
                'ext_ior': 'air',
                'specular_transmittance': {
                    'type': 'rgb',
                    'value': [0.2, 0, 0.2]
            },
            },
        }
        my_scene['object'+str(i)] = object

    scene = mitsuba.load_dict(my_scene)    

    bbox = scene.bbox()

    center = (bbox.min + bbox.max) / 2

    size_x = bbox.max.x - bbox.min.x
    size_y = bbox.max.y - bbox.min.y
    size_z = bbox.max.z - bbox.min.z

    return center, [size_x, size_y, size_z]

def main():
    sensor = load_sensor(45)

    scene = load_scene(light_radiance=100, constant_radiance=0, add_floor=True, add_object=True)
    image = mitsuba.render(scene, spp=224, sensor=sensor)
    mitsuba.util.write_bitmap("result" + ".png", image)
    
    
if __name__ == "__main__":
    main()