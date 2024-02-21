import sys
import os
import json
import re
import copy
import cv2 as cv
import mitsuba
from scene import Scene
from object import Object


mitsuba.set_variant("scalar_rgb")
from mitsuba import ScalarTransform4f as T

class Output:
    def __init__(self, config_file, results_folder):

        with open(config_file, 'r') as file:
            self.data = json.load(file)

        self.config = config_file

        if(not os.path.exists(results_folder)):
            try:
                os.mkdir(results_folder)
            except OSError as error:
                print(error)

        self.results_folder = results_folder


class ImageOutput(Output):
    def __init__(self, config_file, results_folder, result_image_name, angle=0):
        Output.__init__(self, config_file, results_folder)
        self.result_image_name = result_image_name
        self.angle = angle

        objects = []
        scene = Scene(self.config, objects)
        image = mitsuba.render(scene.load_scene(), spp=scene.camera.samples_per_pixel, sensor=scene.camera.load_sensor(angle))

        mitsuba.util.write_bitmap(self.results_folder + result_image_name, image)

class RotationVideo(Output):
     def __init__(self, config_file, results_folder, result_frames_folder, result_video_name):
        Output.__init__(self, config_file, results_folder)

        if(not os.path.exists(results_folder+result_frames_folder)):
            try:
                os.mkdir(results_folder+result_frames_folder)
            except OSError as error:
                print(error)

        output_json = self.data['output']
        step = output_json['rotation_step']
        degrees = output_json['rotation_degrees']
        objects = []
        for i in range(0, degrees, step):
            scene = Scene(self.config, objects)
            image = mitsuba.render(scene.load_scene(), spp=scene.camera.samples_per_pixel, sensor=scene.camera.load_sensor(i))

            mitsuba.util.write_bitmap(self.results_folder + result_frames_folder + str(i) + ".png", image)

class AnimationVideo(Output):
    def __init__(self, config_file, results_folder, result_frames_folder, result_video_name, angle=0):
        Output.__init__(self, config_file, results_folder)

        if(not os.path.exists(results_folder+result_frames_folder)):
            try:
                os.mkdir(results_folder+result_frames_folder)
            except OSError as error:
                print(error)

        objects_json = self.data['objects']

        objects = []
        folders = []
        folders_json = []

        for object_json in objects_json:
            if os.path.isfile(object_json['filename']):
                object = Object(object_json)
                objects.append(object) 
            elif os.path.isdir(object_json['filename']):
                folders.append(os.listdir(object_json['filename']))
                folders_json.append(object_json)

        for i in range(len(folders[0])):
            print("Rendering frame " + str(i+1) + " out of " + str(len(folders[0])))
            objects_tmp = copy.deepcopy(objects)
            for folder_idx in range(len(folders)):
                folders[folder_idx].sort(key=self.natural_keys) 

                filename = folders_json[folder_idx]['filename'] + folders[folder_idx][i]
                
                new_folder_json = copy.deepcopy(folders_json[folder_idx])
                new_folder_json['filename'] = filename
                
                objects_tmp.append(Object(new_folder_json))

            scene = Scene(self.config, objects_tmp)
            image = mitsuba.render(scene.load_scene(), spp=scene.camera.samples_per_pixel, sensor=scene.camera.load_sensor(angle))
            mitsuba.util.write_bitmap(self.results_folder + result_frames_folder + str(i) + ".png", image)

    def atoi(self, text):
        return int(text) if text.isdigit() else text

    def natural_keys(self, text):
        return [self.atoi(c) for c in re.split(r'(\d+)', text) ]
        
