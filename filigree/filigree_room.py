import mitsuba
import numpy as np
import sys

sys.path.append('../')
import variables
import config as cf

config = sys.argv[1]

variables.config = cf.Config(config)

if(variables.config.use_gpu):
    mitsuba.set_variant("cuda_ad_rgb")
else:
    if(variables.config.disable_cpu_parallelization == True):
        mitsuba.set_variant("scalar_rgb")
    else:
        mitsuba.set_variant("llvm_ad_rgb")

from mitsuba import ScalarTransform4f as T

camera_offset_y_axis_multiplier = 1/2 
camera_offset_z_axis_multiplier = 1.5
def load_sensor():
    center, sizes = find_center_of_bounding_box()

    return mitsuba.load_dict({
        'type': 'perspective',
        'fov': variables.config.fov,
        'to_world': T.look_at(origin=[center[0],center[1]+max(sizes)*camera_offset_y_axis_multiplier,center[2]-max(sizes)*camera_offset_z_axis_multiplier], target=center, up=[0, 1, 0]),
        'sampler': {
            'type': 'multijitter',
            'sample_count': 16,
            'seed': variables.config.seed
        },
        'film': {
            'type': 'hdrfilm',
            'width': variables.config.width,
            'height': variables.config.height,
            'rfilter': {
                'type': 'tent',
            },
            'pixel_format': 'rgb',
        },
    })

def load_scene_lights(light_radiance, center, sizes, height):
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

    return my_scene

def load_scene(light_radiance=10):

    center, sizes = find_center_of_bounding_box()
    room_x = sizes[0]
    room_y = sizes[2]*2
    height = max(sizes)

    my_scene = load_scene_lights(light_radiance, center, sizes, height)

    object = {
        'type': 'obj',
        'filename': variables.config.filigree_path,
        'to_world': T.rotate([1,0,0],-90),
        'bsdf': {
            'type': 'conductor',
            'material': 'Al'
        },
    }
    my_scene['skeleton'] = object

    floor = {
        'type': 'rectangle',
        'to_world': T.translate([center[0],center[1]-sizes[1],center[2]]).rotate([1,0,0],-90).scale([room_x,room_y,1]),
        
        'bsdf': {
            'type': 'diffuse',
            'reflectance': {
                'type': 'checkerboard',
                "to_uv": T.scale([10, 10, 0])
            }
        }
    }
    my_scene['floor'] = floor

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
            'filename': variables.config.filigree_path,
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
    sensor = load_sensor()

    scene = load_scene(light_radiance=variables.config.room_lights_radiance)
    image = mitsuba.render(scene, spp=variables.config.samples_per_pixel, sensor=sensor)
    if(variables.config.results_folder == ""):
        mitsuba.util.write_bitmap("result" + ".png", image)
    else:
        mitsuba.util.write_bitmap(variables.config.results_folder + "/result" + ".png", image)
    
    
if __name__ == "__main__":
    main()