format compact
close all; clear; clc;

%% Get input image & output folder
[filename, pathname] = uigetfile({'*.jpg;*.png', 'Image Files (*.jpg, *.png)'}, 'Select pattern image');

if (filename == 0) % cancel pressed
    return;
end  

image_filename = char(sprintf("%s%s",pathname,filename));

I = double(imread(image_filename))/255;
grayImg = rgb2gray(I);
binaryImg = imbinarize(grayImg);

sigma = 1; % Adjust this value based on your needs
smoothedImage = imgaussfilt(grayImg, sigma);

% Get the size of the image
[M, N, ~] = size(I);

% Generate vertex coordinates
[X, Y] = meshgrid(1:N, 1:M);
Z = zeros(size(X)); % Flat surface; for 3D surface use actual z-values
vertices = [X(:) Y(:) Z(:)];

% Create the delaunay triangulation
DT = delaunayTriangulation(vertices(:,1), vertices(:,2));

% Get the connectivity list (triangles)
faces = DT.ConnectivityList;

% Write to an OBJ file
filename = 'image_surface.obj';
fid = fopen(filename, 'w');

% Write vertices
for i = 1:size(vertices, 1)
    if(smoothedImage(vertices(i, 1), vertices(i, 2))>0.99)
        fprintf(fid, 'v %f %f %f\n', vertices(i, 1), vertices(i, 2), vertices(i, 3));
    else
        fprintf(fid, 'v %f %f %f\n', vertices(i, 1), vertices(i, 2), vertices(i, 3)-(1/smoothedImage(vertices(i, 1), vertices(i, 2))));
    end
end

% Write faces
for i = 1:size(faces, 1)
    fprintf(fid, 'f %d %d %d\n', faces(i, 1), faces(i, 2), faces(i, 3));
end

fclose(fid);