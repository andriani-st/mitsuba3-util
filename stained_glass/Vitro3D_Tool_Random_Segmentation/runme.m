format compact
close all; clear; clc;

%% Get input image & output folder
[filename, pathname] = uigetfile({'*.jpg;*.png', 'Image Files (*.jpg, *.png)'}, 'Select an Image');

if (filename == 0) % cancel pressed
    return;
end  

image_filename = char(sprintf("%s%s",pathname,filename));

% get output directory
dataset_output_directory = uigetdir('.', 'Select output directory');
if (dataset_output_directory == 0) % cancel pressed
    return;
end     

%% Get number of tiles
prompt = {'Enter the number of tiles:', 'Enter the distortion factor:'};
dlgtitle = 'Options';
dims = [1 35];
definput = {'500', '0.1'};

answer = inputdlg(prompt, dlgtitle, dims, definput);
if(isempty(answer))
    return;
end
n = str2double(answer{1});
distortionFactor = str2double(answer{2});


%% Random segmentation
I = double(imread(image_filename));%/255;
R = double(imread(image_filename));


% Get the size of the image
[height, width, ~] = size(I);

[skeletonPoints, frameEdges] = getFrameInfo(height, width, 20);
skeletonPoints = [skeletonPoints(:,2) skeletonPoints(:,1)];

piecesEdges = [];
numPoints = size(skeletonPoints,1);
numOuterSkeletonPoints = size(skeletonPoints,1);

x = round(1 + rand([1 n]) * (size(I,2)-2));
y = round(1 + rand([1 n]) * (size(I,1)-2));
[vx,vy] = voronoi(x,y);

[voroimage,sub_image]=voronoizone(x,y,I);

binaryImage = false(size(I,2),size(I,1));
polygonPoints = [];

colorsTxt = sprintf("%s/%s",dataset_output_directory,'colors.txt');
fileObjCol = fopen(colorsTxt,'w');

tilesFolder = sprintf("%s/tiles", dataset_output_directory);
mkdir(tilesFolder);

for i = 1:n
    
    tileFilename = sprintf("%s/%s%s",tilesFolder,num2str(i,'%03d'),'.obj');
    fileObj = fopen(tileFilename,'w');
    
    inds = find(voroimage == voroimage(y(i),x(i)));

    [py1,px1] = ind2sub(size(voroimage),inds);
    
    dt = delaunayTriangulation(px1, py1);
    offset = size(dt.Points,1);
    
    newPoints = scaleTile(dt.Points, 0.8, 0.8);
    
    verticesSurface0 = [];
    verticesSurface1 = [];
    for j=1:size(dt.Points,1)
        new_vertex = [newPoints(j,1), newPoints(j,2),0];
        new_vertex = new_vertex + randn(1, 3) * distortionFactor;
        verticesSurface0 = [verticesSurface0; new_vertex];
        
        new_vertex = [newPoints(j,1), newPoints(j,2),30];
        new_vertex = new_vertex + randn(1, 3) * distortionFactor;
        verticesSurface1 = [verticesSurface1; new_vertex];
    end
    vertices = [verticesSurface0; verticesSurface1];
    
    
    facesSurface0 = [];
    facesSurface1 = [];
    for j=1:size(dt.ConnectivityList,1)
        new_face = [dt.ConnectivityList(j,3), dt.ConnectivityList(j,2), dt.ConnectivityList(j,1)];
        facesSurface0 = [facesSurface0; new_face];
        
        new_face = [dt.ConnectivityList(j,1)+offset, dt.ConnectivityList(j,2)+offset, dt.ConnectivityList(j,3)+offset];
        facesSurface1 = [facesSurface1; new_face];
    end
    faces = [facesSurface0; facesSurface1];
    
    
    k = boundary(dt.Points(:,1),dt.Points(:,2));
    
    boundaries = boundary(newPoints);
    polygonBoundaryPoints = [newPoints(boundaries,2),newPoints(boundaries,1)];
    polygonBoundaryPoints = polygonBoundaryPoints(1:2:end,:);
    
    %% Write to colors file
    mask = poly2mask(polygonBoundaryPoints(:, 1), polygonBoundaryPoints(:, 2), size(I,2), size(I,1));
    binaryImage = binaryImage | mask;
    mask_logical = logical(mask);
    
    masked_R = R(:,:,1) .* mask_logical';
    masked_G = R(:,:,2) .* mask_logical';
    masked_B = R(:,:,3) .* mask_logical';

    % Calculate the mean of the non-zero values in each channel
    mean_R = mean(masked_R(masked_R > 0));
    mean_G = mean(masked_G(masked_G > 0));
    mean_B = mean(masked_B(masked_B > 0));
    
    if isnan(mean_R)
        mean_R = 0;
    end
    if isnan(mean_G)
        mean_G = 0;
    end
    if isnan(mean_B)
        mean_B = 0;
    end
    
    fprintf(fileObjCol, '%f %f %f\n', mean_R, mean_G, mean_B);
    
    %% Add boundary points of tile to skeleton points set
    
    
    

    skeletonPoints = [skeletonPoints; polygonBoundaryPoints];
    sep = [NaN NaN];
    mypoints = [polygonBoundaryPoints; sep];
    polygonPoints = [polygonPoints; mypoints];
    
    numPoints = numPoints + size(polygonBoundaryPoints,1);
    thisEdges = [(numPoints-size(polygonBoundaryPoints,1)+1:numPoints-1)', (numPoints-size(polygonBoundaryPoints,1)+2:numPoints)'; numPoints, numPoints-size(polygonBoundaryPoints,1)+1];
    
    piecesEdges = [piecesEdges; thisEdges];

    for j=1:length(k)-1
        new_face = [k(j), k(j+1), k(j)+offset];
        faces = [faces; new_face];
        
        new_face = [k(j+1), k(j)+offset, k(j+1)+offset];
        faces = [faces; new_face];
    end
    
    %%
    % Compute face normals
    face_normals = cross(vertices(faces(:, 2), :) - vertices(faces(:, 1), :), ...
                            vertices(faces(:, 3), :) - vertices(faces(:, 1), :));

    vertex_normals = zeros(size(vertices));
    for k = 1:size(faces, 1)
        for j = 1:3
            vertex_normals(faces(k, j), :) = vertex_normals(faces(k, j), :) + face_normals(k, :);
        end
    end

    % Normalize vertex normals
    vertex_normals = vertex_normals ./ vecnorm(vertex_normals, 2, 2);
    
    % Writing the obj file...
    fprintf(fileObj, '# Vertices\n');
    fprintf(fileObj, 'v %f %f %f\n', vertices');

    fprintf(fileObj, '# Vertex Normals\n');
    fprintf(fileObj, 'vn %f %f %f\n', vertex_normals');

    fprintf(fileObj, '# Faces\n');
    fprintf(fileObj, 'f %d//%d %d//%d %d//%d\n', [faces, faces]');
end

%%
%figure; plot(skeletonPoints(:,2), skeletonPoints(:,1), 'ro', 'MarkerSize',1);

constrainedEdges = [frameEdges; piecesEdges];
dt = delaunayTriangulation(skeletonPoints(:,2),skeletonPoints(:,1), piecesEdges);

triangulationVertices = dt.Points;
triangulationFaces = dt.ConnectivityList;
%figure; imshow(binaryImage'); hold on; scatter(triangulationVertices(:, 1), triangulationVertices(:, 2), 10, 'b', 'filled');
%patch('Vertices', triangulationVertices, 'Faces', triangulationFaces, 'FaceColor', 'none', 'EdgeColor', 'b');
%hold off;

% Calculate midpoints of each face
midpoints = (triangulationVertices(triangulationFaces(:, 1), :) + ...
             triangulationVertices(triangulationFaces(:, 2), :) + ...
             triangulationVertices(triangulationFaces(:, 3), :)) / 3;
         
%scatter(midpoints(:, 1), midpoints(:, 2), 10, 'g', 'filled');

% Identify midpoints inside the white regions
%[row, col] = find(binaryImage');
%plot(points(:,2), points(:,1));
isMidpointInsideWhite = inpolygon(midpoints(:, 1), midpoints(:, 2), polygonPoints(:,2), polygonPoints(:,1));

%scatter(midpoints(isMidpointInsideWhite, 1), midpoints(isMidpointInsideWhite, 2), 10, 'g', 'filled');

% Identify faces where midpoints are inside the white regions
facesOutsideWhite = ~isMidpointInsideWhite;

patch('Vertices', triangulationVertices, 'Faces', triangulationFaces(facesOutsideWhite, :), 'FaceColor', 'none', 'EdgeColor', 'r'); hold off;

newFaces = triangulationFaces(facesOutsideWhite, :);
% Display the new triangulation
%figure;
%trisurf(newFaces, triangulationVertices(:, 1), triangulationVertices(:, 2), zeros(size(triangulationVertices, 1), 1), 'FaceColor', 'interp', 'EdgeColor', 'k');
%axis equal;
%title('Triangulation without Vertices in White Regions');

%figure;
%triplot(dt, 'b', 'LineWidth', 2);

skeletonV = [triangulationVertices zeros(size(triangulationVertices,1),1)];
skeletonV = [skeletonV; [triangulationVertices ones(size(triangulationVertices,1),1)*30]];

skeletonF = [newFaces; newFaces+size(triangulationVertices,1)];

%% Create faces for connecting the two parts of the skeleton
pointsIndicesFrame0 = 1:numOuterSkeletonPoints;
pointsIndicesFrame1 = size(triangulationVertices,1)+1:size(triangulationVertices,1)+numOuterSkeletonPoints;

newFaces = [];
for i=1:numOuterSkeletonPoints
    if(i+1>numOuterSkeletonPoints)
       j = 1; 
    else
       j = i+1;
    end
    face = [pointsIndicesFrame1(i), pointsIndicesFrame1(j), pointsIndicesFrame0(i)];
    newFaces = [newFaces; face];
    face = [pointsIndicesFrame0(i), pointsIndicesFrame0(j), pointsIndicesFrame1(j)];
    newFaces = [newFaces; face];
end


%% Face normals for skeleton
% Compute face normals
face_normals_skeleton = cross(skeletonV(skeletonF(:, 2), :) - skeletonV(skeletonF(:, 1), :), ...
                        skeletonV(skeletonF(:, 3), :) - skeletonV(skeletonF(:, 1), :));

vertex_normals_skeleton = zeros(size(skeletonV));
for k = 1:size(skeletonF, 1)
    for j = 1:3
        vertex_normals_skeleton(skeletonF(k, j), :) = vertex_normals_skeleton(skeletonF(k, j), :) + face_normals_skeleton(k, :);
    end
end

% Normalize vertex normals
vertex_normals_skeleton = vertex_normals_skeleton ./ vecnorm(vertex_normals_skeleton, 2, 2);
vertex_normals_skeleton(1:size(vertex_normals_skeleton)/2,:) = -vertex_normals_skeleton(1:size(vertex_normals_skeleton)/2,:);

% Plot the mesh with vertex normals
%figure; view(3); rotate3d('on')
%trisurf(skeletonF, skeletonV(:, 1), skeletonV(:, 2), skeletonV(:, 3), 'FaceColor', 'cyan');
%hold on;
%quiver3(skeletonV(:, 1), skeletonV(:, 2), skeletonV(:, 3), ...
%    vertex_normals_skeleton(:, 1), vertex_normals_skeleton(:, 2), vertex_normals_skeleton(:, 3), 'r');
%hold off;
%axis equal;
%xlabel('X');
%ylabel('Y');
%zlabel('Z');
%title('Mesh with Vertex Normals');

skeletonF = [skeletonF; newFaces];

%% Create obj file for the skeleton
skeletonObj = sprintf("%s/%s",dataset_output_directory,'skeleton.obj');
fileObjs = fopen(skeletonObj,'w');
% Writing the obj file for the skeleton...
fprintf(fileObjs, '# Vertices\n');
fprintf(fileObjs, 'v %f %f %f\n', skeletonV');

fprintf(fileObjs, '# Vertex Normals\n');
fprintf(fileObjs, 'vn %f %f %f\n', vertex_normals_skeleton');
 
fprintf(fileObjs, '# Faces\n');
fprintf(fileObjs, 'f %d//%d %d//%d %d//%d\n', [skeletonF, skeletonF]');

close all; clear; clc;
