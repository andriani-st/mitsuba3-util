%{ 
---------------------------------------------------------------------------
                    GetVitroImage3D_Tiles()
---------------------------------------------------------------------------
%}
function binaryImage = GetVitroImage3D_Tiles(image, imagePath, imageOutputFolder, thickness, PADSIZE)
    tic; % Start a stopwatch timer
    fprintf('GetVitroImage3D_Tiles for image %s. Please wait...\n', imagePath);
    
    addpath github_repo
    addpath github_repo/docde

    loadRun = 0;  % todo: 0
    shrinkFactor = 1;

    %% Get distortion factor
    prompt = {'Enter the distortion factor:'};
    dlgtitle = 'Distortion factor';
    dims = [1 35];
    definput = {'0.1'};

    answer = inputdlg(prompt, dlgtitle, dims, definput);
    if(isequal(answer,0))
        return;
    end
    distortionFactor = str2double(answer{1});
       
%     scaleT = .95;
    numPointsPerEdge = 20;
    dthresh = 2;
    mnadj=10; RMThresh=5;%3.5;
    verbose = 0;
    writeTiles = 1;
    compColors = 1;
    erodeSiz = 11;

%     fname = 'image.jpg';
%     image = imread(imagePath);

    if verbose
        figure; imagesc(image); axis image; title('image');
    end

    if loadRun
        load
    else
        I = double(image);
        fprintf('RegionGrowing. Please wait...\n');
        [Region1 Region2 Region3 Region4]=RegionGrowing(image);
        RegionResult=RegionMerging(image,Region1,mnadj,RMThresh);
        n = max(max(RegionResult));
        save
    end



    % Get the size of the image
    [skeletonPoints, frameEdges] = getFrameInfo(size(I,1), size(I,2), numPointsPerEdge,verbose);
%     piecesEdges = [];
%     numPoints = size(skeletonPoints,1);
%     numOuterSkeletonPoints = size(skeletonPoints,1);

    binaryImage = false(size(I,1),size(I,2));
%     polygonPoints = [];

    if compColors && writeTiles
        fileObjCol = fopen(sprintf('%s/colors.txt', imageOutputFolder),'w');
    end
    ws = warning('off','all');  % Turn off warning
    tilesOutputFolder = sprintf('%s/tiles', imageOutputFolder);
    mkdir(tilesOutputFolder);
    warning(ws);  % Turn it back on    
    for i = 1:n
        fprintf('Creating tile %d/%d (%.1f%%)\n', ...
                    i, n, double(i)/double(n)*100);
        tileFilename = sprintf('%s/%03d.obj', tilesOutputFolder, i);
%         tileFilename = ['tiles/' num2str(i,'%03d') '.obj'];
        inds = find(RegionResult == i);
        [binds,inds] = erodeContour2(size(I),inds,erodeSiz,verbose);
        [py1,px1] = ind2sub(size(image),inds);

        dt = delaunayTriangulation(px1, py1);
        offset = size(dt.Points,1);
        validTris = findValidTris(dt,dthresh);
        ConnectivityList = dt.ConnectivityList(validTris,:);
        [vertices,faces,polygonBoundaryPoints] = createTile(tileFilename,dt.Points,binds,ConnectivityList,offset,thickness,distortionFactor,verbose);
        % karam: increase vertices (x,y) coordinates by PADSIZE for padding
        % that will be done in GetVitroImage3D_Skeleton() and in order to
        % synchronize tiles and skeleton coordinates
        vertices = [vertices(:,1)+PADSIZE, vertices(:,2)+PADSIZE, vertices(:,3)];
        if compColors
            % Write to colors file
            %mask = poly2mask(polygonBoundaryPoints(:, 1), polygonBoundaryPoints(:, 2), size(I,2), size(I,1));
            mask = zeros(size(I,1),size(I,2));
            mask(inds) = 1;
            binaryImage = binaryImage | mask;
            if writeTiles
                [mean_R,mean_G,mean_B] = getPolyMeanColor(I,mask);
                fprintf(fileObjCol, '%f %f %f\n', mean_R, mean_G, mean_B);
            end
        end

        lenF = size(faces,1);
        k = boundary(dt.Points(:,1),dt.Points(:,2),shrinkFactor);
        for j=1:length(k)-1
            new_face = [k(j)+offset, k(j+1), k(j)];
            faces = [faces; new_face];
            new_face = [k(j+1), k(j)+offset, k(j+1)+offset];
            faces = [faces; new_face];
        end

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
        %vertex_normals = vertex_normals ./ vecnorm(vertex_normals, 2, 2);
        for k=1:size(vertex_normals,1)
            vertex_normals(k,:) = vertex_normals(k,:) / ...
                sqrt(vertex_normals(k,1)^2 + vertex_normals(k,2)^2 + vertex_normals(k,3)^2);
        end

        if verbose
            figure; hold on;
            plot3(vertices(:,1),vertices(:,2),vertices(:,3),'.');
            for iface = lenF:size(faces,1)
                tri = faces(iface,:);
                p1 = vertices(tri(1),:);
                p2 = vertices(tri(2),:);
                p3 = vertices(tri(3),:);
                plot3([p1(1) p2(1)],[p1(2) p2(2)],[p1(3) p2(3)],'-');
                plot3([p2(1) p3(1)],[p2(2) p3(2)],[p2(3) p3(3)],'-');
                plot3([p3(1) p1(1)],[p3(2) p1(2)],[p3(3) p1(3)],'-');
            end
            hold off; axis equal; view(3);
        end
        if writeTiles
            writeTile(tileFilename,vertices,vertex_normals,faces);
        end
    end
    if compColors && writeTiles
        fclose(fileObjCol);
    end
    if verbose
        figure; imagesc(binaryImage); colormap(gray); axis image; title('skeleton');
    end
    
    timeElapsedSec = toc; % Read the stopwatch timer  
    %hms = sec2hms(timeElapsedSec);
    fprintf('GetVitroImage3D_Tiles(): timeElapsed = %f sec \n', timeElapsedSec);     
end

