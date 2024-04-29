import mitsuba
import numpy as np
import sys
import json
from matplotlib import pyplot as plt

config = sys.argv[1]

with open(config, 'r') as file:
    data = json.load(file)

use_gpu = True
if('use_gpu' in data):
    use_gpu = data['use_gpu']

if(use_gpu):
    mitsuba.set_variant("cuda_ad_rgb")
else:
    mitsuba.set_variant("llvm_ad_rgb")
    
from mitsuba import ScalarTransform4f as T

output_json = data['output']
files_json = data['files']


tiles_path = files_json["tiles_path"]
skeleton_path = files_json["skeleton_path"]
colors_path = files_json["colors_path"]

colors = []
with open(colors_path, 'r') as file:
    for line in file:
        color_components = [float(component)/255 for component in line.split()]
        colors.append(color_components)

print(colors[0])
n=len(colors)+1

def load_sensor(spp, seed):
    center, sizes = find_center_of_bounding_box()

    return mitsuba.load_dict({
        'type': 'perspective',
        'fov': output_json['fov'],
        'to_world': T.look_at(origin=[center[0],center[1],center[2]-max(sizes)-3500], target=center, up=[0, 1, 0]),
        'principal_point_offset_x': 0,  #normalized principal point, [0,0] -> center of image
        'principal_point_offset_y': 0,
        'sampler': {
            'type': 'multijitter',
            'sample_count': spp,
            'seed': seed
        },
        'film': {
            'type': 'hdrfilm',
            'width': output_json['width'],
            'height': output_json['height'],
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
    room_y = 4000
    
    my_scene = {
        'type': 'scene',
        'id': 'my_scene',
        'integrator': {
            'type': 'path'
        },
        'sky': {
            'type': 'envmap',
            'filename': 'sky_road.hdr'
        },
        'light1': {
            'type': 'sphere',
            'to_world': T.translate([center[0]-sizes[0]+100,center[1]+sizes[1]-100,center[2]-100]).scale([100,100,100]),
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
            'to_world': T.translate([center[0]+sizes[0]-100,center[1]+sizes[1]-100,center[2]-100]).scale([100,100,100]),
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
        'light5': {
            'type': 'sphere',
            'to_world': T.translate([center[0]-sizes[0]+100,center[1]+sizes[1]-100,center[2]-100-2000]).scale([100,100,100]),
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
        'light6': {
            'type': 'sphere',
            'to_world': T.translate([center[0]+sizes[0]-100,center[1]+sizes[1]-100,center[2]-100-2000]).scale([100,100,100]),
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
            'to_world': T.translate([center[0]-sizes[0]+100,center[1]+sizes[1]-100,center[2]-room_y*2+100]).scale([100,100,100]),
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
            'to_world': T.translate([center[0]+sizes[0]-100,center[1]+sizes[1]-100,center[2]-room_y*2+100]).scale([100,100,100]),
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
                #'alpha_v': 0.5
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
            'to_world': T.translate([center[0],center[1]-sizes[1],center[2]-room_y]).rotate([1,0,0],-90).scale([room_x,room_y,1]),
            'bsdf': {
                'type': 'diffuse',
                'reflectance': {
                    'type': 'rgb',
                    'value': [0.1, 0.25, 0.3]
                }
            }
        }
        my_scene['floor'] = floor

    if(1):
        ceiling = {
            'type': 'rectangle',
            'to_world': T.translate([center[0],center[1]+sizes[1],center[2]-room_y]).rotate([1,0,0],90).scale([room_x,room_y,1]),
            'bsdf': {
                'type': 'diffuse',
                'reflectance': {
                    'type': 'rgb',
                    'value': [0.1, 0.25, 0.3]
                }
            }
        }
        my_scene['ceiling'] = ceiling

        back_wall_bottom = {
            'type': 'rectangle',
            'to_world': T.translate([center[0],center[1]-3*sizes[1]/4,center[2]]).rotate([1,0,0],-180).scale([room_x,sizes[1]/4,100]),
            'bsdf': {
                'type': 'diffuse',
                'reflectance': {
                    'type': 'rgb',
                    'value': [0.1, 0.25, 0.3]
                }
            }
        }
        my_scene['back_wall_bottom'] = back_wall_bottom

        back_wall_up = {
            'type': 'rectangle',
            'to_world': T.translate([center[0],center[1]+3*sizes[1]/4,center[2]]).rotate([1,0,0],-180).scale([room_x,sizes[1]/4,100]),
            'bsdf': {
                'type': 'diffuse',
                'reflectance': {
                    'type': 'rgb',
                    'value': [0.1, 0.25, 0.3]
                }
            }
        }
        my_scene['back_wall_up'] = back_wall_up

        back_wall_side1 = {
            'type': 'rectangle',
            'to_world': T.translate([center[0]-3*sizes[0]/4,center[1],center[2]]).rotate([1,0,0],-180).scale([sizes[0]/4,sizes[1],100]),
            'bsdf': {
                'type': 'diffuse',
                'reflectance': {
                    'type': 'rgb',
                    'value': [0.1, 0.25, 0.3]
                }
            }
        }
        my_scene['back_wall_side1'] = back_wall_side1

        back_wall_side2 = {
            'type': 'rectangle',
            'to_world': T.translate([center[0]+3*sizes[0]/4,center[1],center[2]]).rotate([1,0,0],-180).scale([sizes[0]/4,sizes[1],100]),
            'bsdf': {
                'type': 'diffuse',
                'reflectance': {
                    'type': 'rgb',
                    'value': [0.1, 0.25, 0.3]
                }
            }
        }
        my_scene['back_wall_side2'] = back_wall_side2

        side_wall1 = {
            'type': 'rectangle',
            'to_world': T.translate([center[0]+room_x,center[1],center[2]-room_y]).rotate([1,0,0],-180).rotate([0,1,0],-90).scale([room_y,room_x,1]),
            'bsdf': {
                'type': 'diffuse',
                'reflectance': {
                    'type': 'rgb',
                    'value': [0.1, 0.25, 0.3]
                }
            }
        }
        my_scene['side_wall1'] = side_wall1

        side_wall2 = {
            'type': 'rectangle',
            'to_world': T.translate([center[0]-room_x,center[1],center[2]-room_y]).rotate([1,0,0],-180).rotate([0,1,0],90).scale([room_y,room_x,1]),
            'bsdf': {
                'type': 'diffuse',
                'reflectance': {
                    'type': 'rgb',
                    'value': [0.1, 0.25, 0.3]
                }
            }
        }
        my_scene['side_wall2'] = side_wall2

        front_wall = {
            'type': 'rectangle',
            'to_world': T.translate([center[0],center[1],center[2]-room_y*2]).rotate([1,0,0],360).scale([room_x,sizes[1],1]),
            'bsdf': {
                'type': 'diffuse',
                'reflectance': {
                    'type': 'rgb',
                    'value': [0.1, 0.25, 0.3]
                }
            }
        }
        my_scene['front_wall'] = front_wall

    #mesh_params = mitsuba.traverse(mitsuba.load_dict(my_scene))
    #print(mesh_params)

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
    sensor = load_sensor(output_json['samples_per_pixel'], output_json['seed'])

    scene = load_scene(light_radiance=10, constant_radiance=0, add_floor=True, add_object=True)
    image = mitsuba.render(scene, spp=output_json['samples_per_pixel'], sensor=sensor)
    mitsuba.util.write_bitmap("result" + ".png", image)
    
    
if __name__ == "__main__":
    main()