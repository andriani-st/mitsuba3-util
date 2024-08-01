import sys
import os
import cv2 as cv
import time
import variables  
import config as cf
from colorama import Fore, Back, Style

def main():

    folder_json_path = sys.argv[1]
    if(os.path.isfile(folder_json_path)):
        json_files = [folder_json_path]
    else:
        # List all files in the folder
        json_files = os.listdir(folder_json_path)
        json_files = sorted(json_files, key=lambda x: int(''.join(filter(str.isdigit, x))))

    for i in range(1,len(json_files)+1):
        if(os.path.isfile(folder_json_path)):
            config = json_files[i-1]
        else:
            config = os.path.join(folder_json_path, json_files[i-1])

        variables.config = cf.Config(config)
        import output
        
        if variables.config.output_type == "animation_video":
            output.AnimationVideo(variables.config.results_folder, "frames" + str(i) + "/", "video.avi", variables.config.rotation_degrees)
            video=cv.VideoWriter(variables.config.results_folder + "video" + str(i) + ".avi", cv.VideoWriter_fourcc(*'XVID'), variables.config.fps, (variables.config.width,variables.config.width))
            
            folder_path = variables.config.results_folder + "frames" + str(i) + "/"

            # List all files in the folder
            files = os.listdir(folder_path)
            files = sorted(files, key=lambda x: int(''.join(filter(str.isdigit, x))))

            for file in files:
                file_path = os.path.join(folder_path, file)
                video.write(cv.imread(file_path))

            video.release()
        
        elif variables.config.output_type == "rotation_video":
            output.RotationVideo(variables.config.results_folder, "frames" + str(i) + "/", "video" + str(i) + ".avi")
            video=cv.VideoWriter(variables.config.results_folder + "video" + str(i) + ".avi", cv.VideoWriter_fourcc(*'XVID'), variables.config.fps, (variables.config.width,variables.config.width))
            
            folder_path = variables.config.results_folder + "frames" + str(i) + "/"

            # List all files in the folder
            files = os.listdir(folder_path)
            files = sorted(files, key=lambda x: int(''.join(filter(str.isdigit, x))))

            for file in files:
                file_path = os.path.join(folder_path, file)
                video.write(cv.imread(file_path))

            video.release()
        
        elif variables.config.output_type == "image":
            output.ImageOutput(variables.config.results_folder, str(i) + ".png", variables.config.rotation_degrees)
    
if __name__ == "__main__":
    start_time = time.time()
    main()
    print(Fore.LIGHTGREEN_EX + "Rendering completed in %s seconds" % (time.time() - start_time) + Style.RESET_ALL)