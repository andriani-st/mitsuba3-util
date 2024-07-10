%{ 
---------------------------------------------------------------------------
                    Vitro3D_Tool()
---------------------------------------------------------------------------
%}
function Vitro3D_Tool()
    format compact;
    close all; clear; clc;

    % fill Vitro3D_Tool_Config
    Vitro3D_Tool_Config.thickness = 30;
    Vitro3D_Tool_Config.PADSIZE = 10;   
    % get input directory
    Vitro3D_Tool_Config.dataset_input_directory = uigetdir('.', 'Select input directory');
    if (Vitro3D_Tool_Config.dataset_input_directory == 0) % cancel pressed
        return;
    end  
    % get output directory
    Vitro3D_Tool_Config.dataset_output_directory = uigetdir('.', 'Select output directory');
    if (Vitro3D_Tool_Config.dataset_output_directory == 0) % cancel pressed
        return;
    end     
    
    imageFiles=[dir(sprintf('%s/*.jpg', Vitro3D_Tool_Config.dataset_input_directory));...
        dir(sprintf('%s/*.png', Vitro3D_Tool_Config.dataset_input_directory))];

    imageFilesSize = size(imageFiles, 1);
    for i=1:imageFilesSize % for each image of dataset_input_directory: GetVitroImage3D()
        imageName = imageFiles(i).name;
        imagePath = sprintf('%s/%s', Vitro3D_Tool_Config.dataset_input_directory, imageName);
        imageOutputFolder = strrep(imageName, '.', '_');
        imageOutputFolder = sprintf('%s/%s', Vitro3D_Tool_Config.dataset_output_directory, imageOutputFolder);
        ws = warning('off','all');  % Turn off warning
        mkdir(imageOutputFolder);
        warning(ws);  % Turn it back on
        fprintf('Creating 3D for image %s %d/%d (%.1f%%)...\n', ...
                    imagePath, i, imageFilesSize, double(i)/double(imageFilesSize)*100);        
        GetVitroImage3D(imagePath, imageOutputFolder, Vitro3D_Tool_Config);        
    end
  
%     imagePath = 'image.jpg';
%     GetVitroImage3D(imagePath, Vitro3D_Tool_Config);    
end

