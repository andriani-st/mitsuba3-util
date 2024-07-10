close all; clear; clc;

load('afterTiles.mat');
binaryImage = imread('a.png');
%     binaryImage = binaryImage(150:250, 70:250); % <--- for a.png
    binaryImage = padarray(binaryImage,[PADSIZE,PADSIZE]);
    
%     binaryImage = binaryImage(200:250, 130:230); % <--- for a.png
%     binaryImage = binaryImage(200:230, 200:230); % <--- for a.png
verbose = 0;
if verbose
    figure; imagesc(binaryImage); colormap(gray); axis image; title('skeleton cutted');
end
GetVitroImage3D_Skeleton(binaryImage, imageOutputFolder, thickness, PADSIZE);
