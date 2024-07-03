%{ 
---------------------------------------------------------------------------
                    GetVitroImage3D()
---------------------------------------------------------------------------
%}
function GetVitroImage3D(imagePath, imageOutputFolder, Vitro3D_Tool_Config)
    thickness = Vitro3D_Tool_Config.thickness;
    PADSIZE = Vitro3D_Tool_Config.PADSIZE;
    
    % load image
    image = imread(imagePath);
    % create tiles 3D and get binaryImage
    binaryImage = GetVitroImage3D_Tiles(image, imagePath, imageOutputFolder, thickness, PADSIZE);
    % create skeleton 3D
    GetVitroImage3D_Skeleton(binaryImage, imageOutputFolder, thickness, PADSIZE);
end

