import sys
import os
import json
import cv2 as cv
import time
import variables  

def main():

    folder_json_path = sys.argv[1]
    if(os.path.isfile(folder_json_path)):
        json_files = [folder_json_path]
    else:
        # List all files in the folder
        json_files = os.listdir(folder_json_path)
        json_files = sorted(json_files, key=lambda x: int(''.join(filter(str.isdigit, x))))

    for i in range(1,len(json_files)+1):
        print("Processing", json_files[i-1])

        if(os.path.isfile(folder_json_path)):
            config = json_files[i-1]
        else:
            config = os.path.join(folder_json_path, json_files[i-1])
        with open(config, 'r') as file:
            data = json.load(file)

        if('use_gpu' in data):
            variables.use_gpu = data['use_gpu']
        import output

        output_json = data['output']
        
        if output_json['type'] == "animation_video":
            output.AnimationVideo(config, output_json["results_folder"], "frames" + str(i) + "/", "video.avi", output_json['rotation_degrees'])
        elif output_json['type'] == "rotation_video":
            output.RotationVideo(config, output_json["results_folder"], "frames" + str(i) + "/", "video" + str(i) + ".avi")
            video=cv.VideoWriter(output_json["results_folder"] + "video" + str(i) + ".avi",cv.VideoWriter_fourcc(*'XVID'),5,(512,512))
            
            folder_path = output_json["results_folder"] + "frames" + str(i) + "/"

            # List all files in the folder
            files = os.listdir(folder_path)
            files = sorted(files, key=lambda x: int(''.join(filter(str.isdigit, x))))

            for file in files:
                file_path = os.path.join(folder_path, file)
                video.write(cv.imread(file_path))

            video.release()
        
        elif output_json['type'] == "image":
            output.ImageOutput(config, output_json["results_folder"], str(i) + ".png", output_json['rotation_degrees'])
    
if __name__ == "__main__":
    main()