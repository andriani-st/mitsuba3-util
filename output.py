import os
import re
import copy
import mitsuba
import numpy as np
from config import ObjectConfig
from variables import *

from scene import Scene
from object import Object

class Output:
    def __init__(self, results_folder):
        if(not os.path.exists(results_folder) and results_folder):
            try:
                os.mkdir(results_folder)
            except OSError as error:
                print(error)

        self.results_folder = results_folder


class ImageOutput(Output):
    def __init__(self, results_folder, result_image_name, angle=0):
        Output.__init__(self, results_folder)
        self.result_image_name = result_image_name
        self.angle = angle

        objects = []
        scene = Scene(objects)
        image = mitsuba.render(scene.load_scene(), spp=scene.camera.samples_per_pixel, sensor=scene.camera.load_sensor(angle))

        mitsuba.util.write_bitmap(self.results_folder + result_image_name, image)

class RotationVideo(Output):
     def __init__(self, results_folder, result_frames_folder, result_video_name):
        Output.__init__(self, results_folder)

        if(not os.path.exists(results_folder+result_frames_folder)):
            try:
                os.mkdir(results_folder+result_frames_folder)
            except OSError as error:
                print(error)

        step = config.rotation_step
        degrees = config.rotation_degrees
        objects = []
        frame_idx = 1
        for i in np.arange(0, degrees, step):
            print("Rendering frame " + str(frame_idx) + " out of " + str(int(degrees/step)))
            scene = Scene(objects)
            image = mitsuba.render(scene.load_scene(), spp=scene.camera.samples_per_pixel, sensor=scene.camera.load_sensor(i))

            mitsuba.util.write_bitmap(self.results_folder + result_frames_folder + str(i) + ".png", image)
            frame_idx += 1

class AnimationVideo(Output):
    def __init__(self, results_folder, result_frames_folder, result_video_name, angle=0):
        Output.__init__(self, results_folder)

        if(not os.path.exists(results_folder+result_frames_folder)):
            try:
                os.mkdir(results_folder+result_frames_folder)
            except OSError as error:
                print(error)

        objects_json = config.objects

        objects = []
        folders = []
        folders_json = []

        object_json : ObjectConfig
        for object_json in objects_json:
            if os.path.isfile(object_json.filename):
                object = Object(object_json)
                objects.append(object) 
            elif os.path.isdir(object_json.filename):
                folders.append(os.listdir(object_json.filename))
                folders_json.append(object_json)

        if(len(folders) != 0):
            frames_num = len(folders[0])
        else:
            frames_num = 1

        for i in range(frames_num):
            print("Rendering frame " + str(i+1) + " out of " + str(frames_num))
            objects_tmp = copy.deepcopy(objects)
            for folder_idx in range(len(folders)):
                folders[folder_idx].sort(key=self.natural_keys) 

                filename = folders_json[folder_idx].filename + folders[folder_idx][i]
                
                new_folder_json = copy.deepcopy(folders_json[folder_idx])
                new_folder_json.filename = filename
                
                objects_tmp.append(Object(new_folder_json))

            scene = Scene(objects_tmp)
            image = mitsuba.render(scene.load_scene(), spp=scene.camera.samples_per_pixel, sensor=scene.camera.load_sensor(angle))
            mitsuba.util.write_bitmap(self.results_folder + result_frames_folder + str(i) + ".png", image)

    def atoi(self, text):
        return int(text) if text.isdigit() else text

    def natural_keys(self, text):
        return [self.atoi(c) for c in re.split(r'(\d+)', text) ]
        
