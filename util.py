import sys
import os
import json

import output

def main():
    with open("config.json", 'r') as file:
        data = json.load(file)

    output_json = data['output']
    
    if output_json['type'] == "animation_video":
        output.AnimationVideo("config.json", "collection/test_folder/", "frames/", "video.avi")
    elif output_json['type'] == "rotation_video":
        output.RotationVideo("../config.json", "test_folder/", "frames/", "video.avi")
    elif output_json['type'] == "image":
        output.ImageOutput("config.json","test_folder/", "result.png", 0)
    
if __name__ == "__main__":
    main()