import json
from colorama import Fore, Back, Style
import os
import copy

class Config:
    def __init__(self, config_file):
        print(Back.GREEN + "Processing " + config_file + " ..." + Style.RESET_ALL)

        with open(config_file, 'r') as file:
            data = json.load(file) 

        if('disable_cpu_parallelization' in data):
            self.disable_cpu_parallelization = data['disable_cpu_parallelization']
        else:
            self.disable_cpu_parallelization = False

        if('use_gpu' in data):
            self.use_gpu = data['use_gpu']
            if(self.use_gpu == True):
                print(Fore.CYAN + "Running using cuda enabled" + Style.RESET_ALL)
            else:
                if(self.disable_cpu_parallelization == False):
                    print(Fore.CYAN + "Running on CPU only enabled (parallelization on)" + Style.RESET_ALL)
                else:
                    print(Fore.CYAN + "Running on CPU only enabled (parallelization off)" + Style.RESET_ALL)
        else:
            self.use_gpu = True
            print(Fore.CYAN + "Running using cuda enabled \n" + Style.RESET_ALL + "(If you want to run on CPU instead set 'use_gpu' field to false in the configuration file)")
        
        
        
        if('lights_radiance' in data):
            self.room_lights_radiance = data['lights_radiance']
        else:
            self.room_lights_radiance = 10

        if('filigree_path' in data):
            data['output']['type'] = "image"
            self.filigree_path = data['filigree_path']

        if('stained_glass_files' in data):
            data['output']['type'] = "image"
            self.tiles_path = data['stained_glass_files']['tiles_path']
            self.skeleton_path = data['stained_glass_files']['skeleton_path']
            self.colors_path = data['stained_glass_files']['colors_path']

        self.read_output_json_object(data)

        if(not 'filigree_path' in data and not 'stained_glass_files' in data):
            self.read_lights_json_object(data)
            self.read_objects_json_object(data)

        print(Back.GREEN + "Done" + Style.RESET_ALL)
            

    def read_output_json_object(self, data):
        if not 'output' in data:
            raise SystemExit(Fore.RED + "ERROR: Required json object 'output' is missing from configuration file" + Style.RESET_ALL)
                
        output = data['output']

        if not 'type' in output:
            print(Fore.LIGHTYELLOW_EX + "Warning: Output type is not set, setting to default value 'image'" + Style.RESET_ALL)
            self.output_type = "image"
        else:
            if not (output["type"] == "image" or output["type"] == "animation_video" or output["type"] == "rotation_video"):
                raise SystemExit(Fore.RED + "ERROR: Unsuported output type " + output["type"] + Style.RESET_ALL)
            self.output_type = output["type"]

        if not 'results_folder' in output:
            print(Fore.LIGHTYELLOW_EX + "Warning: No folder to save results was selected. Results will be saved in current directory" + Style.RESET_ALL)
            self.results_folder = ""
        else:
            self.results_folder = output['results_folder']

        if not 'results_filename' in output:
            self.results_name = ""
        else:
            self.results_name = output['results_filename']

        if not 'rotation_degrees' in output:
            if output["type"] == "rotation_video":
                self.rotation_degrees = 360
            else:
                self.rotation_degrees = 0
        else:
            self.rotation_degrees = output['rotation_degrees']

        if not 'rotation_step' in output:
            self.rotation_step = 1
        else:
            self.rotation_step = output['rotation_step']

        if not 'width' in output:
            self.width = 512
        else:
            self.width = output['width']

        if not 'height' in output:
            self.height = 512
        else:
            self.height = output['height']

        if not 'fps' in output:
            self.fps = 5
        else:
            self.fps = output['fps']

        if not 'target' in output:
            self.target = "auto"
        else:
            self.target = output['target']

        if not 'origin' in output:
            self.origin = "auto"
        else:
            self.origin = output['origin']

        if not 'distance' in output:
            self.distance = "auto"
        else:
            self.distance = output['distance']
        
        if not 'seed' in output:
            self.seed = 0
        else:
            self.seed = output['seed']

        if not 'fov' in output:
            self.fov = 45
        else:
            self.fov = output['fov']

        if not 'samples_per_pixel' in output:
            self.samples_per_pixel = 224
        else:
            self.samples_per_pixel = output['samples_per_pixel']

        if not 'up_axis' in output:
            self.up_axis = [0,0,1]
        else:
            self.up_axis = output['up_axis']

        if not 'camera_axis' in output:
            self.camera_axis = [0,1,0]
        else:
            self.camera_axis = output['camera_axis']

        if not 'rotation_axis' in output:
            self.rotation_axis = [0,0,1]
        else:
            self.rotation_axis = output['rotation_axis']

        if not 'x_rotation_degrees' in output:
            self.x_rotation_degrees = 0
        else:
            self.x_rotation_degrees = output['x_rotation_degrees'] 

        if not 'y_rotation_degrees' in output:
            self.y_rotation_degrees = 0
        else:
            self.y_rotation_degrees = output['y_rotation_degrees'] 

        if not 'z_rotation_degrees' in output:
            self.z_rotation_degrees = 0
        else:
            self.z_rotation_degrees = output['z_rotation_degrees'] 


        if not 'add_floor' in output:
            self.add_floor = True
        else:
            self.add_floor = output['add_floor']

        if 'floor_type' in output and output['floor_type']=="checkerboard":
            self.floor_type = "checkerboard"
        else:
            self.floor_type = "diffuse"

        if('floor_color' in output):
            self.floor_color = output['floor_color']
        else:
            self.floor_color = [0.1, 0.25, 0.3]

        if not 'add_background' in output:
            self.add_background = False
        else:
            self.add_background = output['add_background']

        if 'background_type' in output and output['background_type']=="checkerboard":
            self.background_type = "checkerboard"
        else:
            self.background_type = "diffuse"

        if('background_color' in output):
            self.background_color = output['background_color']
        else:
            self.background_color = [0.1, 0.25, 0.3]

    def read_lights_json_object(self, data):
        if not 'lights' in data:
            raise SystemExit(Fore.RED + "ERROR: Required json object 'lights' is missing from configuration file" + Style.RESET_ALL)
                
        lights_json = data['lights']
        self.lights = []
        for light_config in lights_json:
            self.lights.append(LightConfig(light_config))

    def read_objects_json_object(self, data):
        if not 'objects' in data:
            raise SystemExit(Fore.RED + "ERROR: Required json object 'objects' is missing from configuration file" + Style.RESET_ALL)
                
        objects_json = data['objects']
        self.objects = []
        for object_config in objects_json:
            if 'filename' in object_config and os.path.isdir(object_config['filename']) and not self.output_type=="animation_video" :
                if 'colors_filename' in object_config:
                    colors = []
                    with open(object_config['colors_filename'], 'r') as file:
                        for line in file:
                            color_components = [float(component)/255 for component in line.split()]
                            colors.append(color_components)

                    n=len(colors)+1
                else:
                    n = len(os.listdir(object_config['filename']))
                    print(n)
                for i in range(1,n):
                    object_i_config = copy.deepcopy(object_config)
                    object_i_config['filename'] = object_config['filename'] + str(i).zfill(3) + '.obj'
                    object_i_config['name'] = 'tile_' + str(i)
                    if 'colors_filename' in object_config:
                        object_i_config['material']['color'] = colors[i-1]
                    
                    self.objects.append(ObjectConfig(object_i_config))
            else:
                self.objects.append(ObjectConfig(object_config))

class LightConfig:
    def __init__(self, light_config_file):
        if not 'emitter_type' in light_config_file:
            raise SystemExit(Fore.RED + "ERROR: Required json field 'emitter_type' is missing from object in 'lights" + Style.RESET_ALL)
        elif not (light_config_file['emitter_type'] == "area" or light_config_file['emitter_type'] == "envmap"):
            raise SystemExit(Fore.RED + "ERROR: Unsuported emitter_type value " + light_config_file['emitter_type'] + Style.RESET_ALL)
        else:
            self.emitter_type = light_config_file['emitter_type']

        if self.emitter_type == 'envmap':
            if 'filename' not in light_config_file:
                raise SystemExit(Fore.RED + "ERROR: 'emitter_type' is envmap and the 'filepath' field is missing" + Style.RESET_ALL)
            elif 'filename' in light_config_file:
                self.envmap_filename = light_config_file['filename']

            if 'rotation_axis' not in light_config_file:
                self.envmap_rotation_axis = [0,0,0]
            else:
                 self.envmap_rotation_axis = light_config_file['rotation_axis']

            if 'rotation_degrees' not in light_config_file:
                self.envmap_rotation_degrees = 0
            else:
                self.envmap_rotation_degrees = light_config_file['rotation_degrees']

            if 'scale_factor' not in light_config_file:
                self.envmap_scale_factor = 0.5
            else:
                self.envmap_scale_factor = light_config_file['scale_factor']
        else:
            if 'radiance' not in light_config_file:
                self.emitter_radiance = 10
            else:
                self.emitter_radiance = light_config_file['radiance']

        if not 'emitter_shape' in light_config_file:
            self.emitter_shape = "sphere"
        else:
            self.emitter_shape = light_config_file['emitter_shape']

        if not 'size' in light_config_file:
            self.emitter_size = "medium"
        else:
            self.emitter_size = light_config_file['size']
            
        if not 'distance_from_object' in light_config_file:
            self.emitter_distance_from_object = "medium"
        else:
            self.emitter_distance_from_object = light_config_file['distance_from_object']

        if not 'position' in light_config_file:
            self.emitter_position = "top-center"
        else:
            self.emitter_position = light_config_file['position']

        if 'rotation_axis' in light_config_file:
            self.emitter_rotation_axis = light_config_file['rotation_axis']
        else:
            self.emitter_rotation_axis = [1,0,0]

        if 'rotation_degrees' in light_config_file:
            self.emitter_rotation_degrees = light_config_file['rotation_degrees']
        else:
            self.emitter_rotation_degrees = 0

class ObjectConfig:
    object_idx = 0
    def __init__(self, object_config_file):
        self.name = 'object_' + str(ObjectConfig.object_idx)
        ObjectConfig.object_idx += 1

        if not 'filename' in object_config_file:
            raise SystemExit(Fore.RED + "ERROR: Required json field 'filename' is missing from object in 'objects" + Style.RESET_ALL)
        else:
            self.filename = object_config_file['filename']

        if not 'type' in object_config_file:
            raise SystemExit(Fore.RED + "ERROR: Required json field 'type' is missing from object in 'objects" + Style.RESET_ALL)
        else:
            self.type = object_config_file['type']

        if not 'rotation_axis' in object_config_file:
            self.rotation_axis = [1,0,0]
        else:
            self.rotation_axis = object_config_file['rotation_axis']

        if not 'rotation_degrees' in object_config_file:
            self.rotation_degrees = 0
        else:
            self.rotation_degrees = object_config_file['rotation_degrees']

        if not 'x_rotation_degrees' in object_config_file:
            self.x_rotation_degrees = 0
        else:
            self.x_rotation_degrees = object_config_file['x_rotation_degrees'] 

        if not 'y_rotation_degrees' in object_config_file:
            self.y_rotation_degrees = 0
        else:
            self.y_rotation_degrees = object_config_file['y_rotation_degrees'] 

        if not 'z_rotation_degrees' in object_config_file:
            self.z_rotation_degrees = 0
        else:
            self.z_rotation_degrees = object_config_file['z_rotation_degrees'] 

        if not 'material' in object_config_file:
            raise SystemExit(Fore.RED + "ERROR: Required json object 'material' is missing from object in 'objects" + Style.RESET_ALL)
        else:
            material = object_config_file['material']

        if not 'type' in material:
            self.material_type = "diffuse"
        else:
            self.material_type = material['type']
            self.material = material

        if not 'color' in material and (self.material_type == "plastic" or self.material_type == "roughplastic"):
            self.material_color = [0.1, 0.27, 0.36]
        elif not 'color' in material:
            self.material_color = "auto"
        else:
            self.material_color = material['color']

        if not 'metal_type' in material:
            self.metal_type = "Au"
        else:
            self.metal_type = material["metal_type"]

        if not 'alpha' in material:
            self.material_alpha = 0.1
        else:
            self.material_alpha = material['alpha']