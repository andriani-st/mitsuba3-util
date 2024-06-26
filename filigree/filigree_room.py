import mitsuba
import numpy as np
import sys
import json

config = sys.argv[1]

with open(config, 'r') as file:
    data = json.load(file)

use_gpu = True
if('use_gpu' in data):
    use_gpu = data['use_gpu']

if(use_gpu):
    print("Running with cuda...")
    mitsuba.set_variant("cuda_ad_rgb")
else:
    mitsuba.set_variant("llvm_ad_rgb")

from matplotlib import pyplot as plt
from mitsuba import ScalarTransform4f as T

filigree_path = data['filigree_path']

def load_sensor(fov):
    center, sizes = find_center_of_bounding_box()

    return mitsuba.load_dict({
        'type': 'perspective',
        'fov': data['output']['fov'],
        'to_world': T.look_at(origin=[center[0],center[1]+max(sizes),center[2]-max(sizes)*1.4], target=center, up=[0, 1, 0]),
        'principal_point_offset_x': 0,  #normalized principal point, [0,0] -> center of image
        'principal_point_offset_y': 0,
        'sampler': {
            'type': 'multijitter',
            'sample_count': 16,
            'seed': data['output']['seed']
        },
        'film': {
            'type': 'hdrfilm',
            'width': data['output']['width'],
            'height': data['output']['height'],
            'rfilter': {
                'type': 'tent',
            },
            'pixel_format': 'rgb',
        },
    })

def load_scene(light_radiance=1, constant_radiance=0, add_floor = True, add_object=True):

    center, sizes = find_center_of_bounding_box()
    side = 200
    room_x = sizes[0]
    room_y = sizes[2]*2
    height = 1000
    print(sizes)

    my_scene = {
        'type': 'scene',
        'id': 'my_scene',
        'integrator': {
            'type': 'path'
        },
        'light1': {
            'type': 'sphere',
            'to_world': T.translate([center[0]-sizes[0]/2,center[1]+height,center[2]-sizes[2]/2]).scale([100,100,100]),
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
        'light2': {
            'type': 'sphere',
            'to_world': T.translate([center[0]+sizes[0]/2,center[1]+height,center[2]-sizes[2]/2]).scale([100,100,100]),
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
            'to_world': T.translate([center[0]-sizes[0]/2,center[1]+height,center[2]+sizes[2]/2]).scale([100,100,100]),
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
        'light4': {
            'type': 'sphere',
            'to_world': T.translate([center[0]+sizes[0]/2,center[1]+height,center[2]+sizes[2]/2]).scale([100,100,100]),
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
            'to_world': T.rotate([1,0,0],-90),
            'bsdf': {
                'type': 'conductor',
                'material': 'Al',
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
        floor = {
            'type': 'rectangle',
            'to_world': T.translate([center[0],center[1]-sizes[1],center[2]]).rotate([1,0,0],-90).scale([room_x,room_y,1]),
            
            'bsdf': {
                'type': 'diffuse',
                'reflectance': {
                    'type': 'checkerboard',
                    "to_uv": T.scale([10, 10, 0])
                    #'value': [0.1, 0.25, 0.3]
                }
            }
        }
        my_scene['floor'] = floor

    if(1):
        ceiling = {
            'type': 'rectangle',
            'to_world': T.translate([center[0],center[1]+height,center[2]]).rotate([1,0,0],90).scale([room_x,room_y,1]),
            'bsdf': {
                'type': 'diffuse',
                'reflectance': {
                    'type': 'rgb',
                    'value': [0.8, 0.8, 0.8]
                }
            }
        }
        my_scene['ceiling'] = ceiling

        back_wall = {
            'type': 'rectangle',
            'to_world': T.translate([center[0],center[1],center[2]+room_y]).rotate([1,0,0],-180).scale([room_x,height,1]),
            'bsdf': {
                'type': 'diffuse',
                'reflectance': {
                    'type': 'rgb',
                    'value': [0.8, 0.8, 0.8]
                }
            }
        }
        my_scene['back_wall'] = back_wall

        side_wall1 = {
            'type': 'rectangle',
            'to_world': T.translate([center[0]+room_x,center[1],center[2]]).rotate([1,0,0],-180).rotate([0,1,0],-90).scale([room_y,height,1]),
            'bsdf': {
                'type': 'diffuse',
                'reflectance': {
                    'type': 'rgb',
                    'value': [0.8, 0.8, 0.8]
                }
            }
        }
        my_scene['side_wall1'] = side_wall1

        side_wall2 = {
            'type': 'rectangle',
            'to_world': T.translate([center[0]-room_x,center[1],center[2]]).rotate([1,0,0],-180).rotate([0,1,0],90).scale([room_y,height,1]),
            'bsdf': {
                'type': 'diffuse',
                'reflectance': {
                    'type': 'rgb',
                    'value': [0.8, 0.8, 0.8]
                }
            }
        }
        my_scene['side_wall2'] = side_wall2

        front_wall = {
            'type': 'rectangle',
            'to_world': T.translate([center[0],center[1],center[2]-room_y]).rotate([1,0,0],360).scale([room_x,height,1]),
            'bsdf': {
                'type': 'diffuse',
                'reflectance': {
                    'type': 'rgb',
                    'value': [0.8, 0.8, 0.8]
                }
            }
        }
        my_scene['front_wall'] = front_wall

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
            'filename': filigree_path,
            'to_world': T.rotate([1,0,0],-90)
        }
    }

    scene = mitsuba.load_dict(my_scene)    

    bbox = scene.bbox()

    center = (bbox.min + bbox.max) / 2

    size_x = bbox.max.x - bbox.min.x
    size_y = bbox.max.y - bbox.min.y
    size_z = bbox.max.z - bbox.min.z

    return center, [size_x, size_y, size_z]

def main():
    sensor = load_sensor(45)

    scene = load_scene(light_radiance=10, constant_radiance=0, add_floor=True, add_object=True)
    image = mitsuba.render(scene, spp=data['output']['samples_per_pixel'], sensor=sensor)
    mitsuba.util.write_bitmap("result" + ".png", image)
    
    
if __name__ == "__main__":
    main()