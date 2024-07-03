%{ 
---------------------------------------------------------------------------
                    GetVitroImage3D_Skeleton()
---------------------------------------------------------------------------
%}
function GetVitroImage3D_Skeleton(binaryImage, imageOutputFolder, thickness, PADSIZE)
    tic; % Start a stopwatch timer
    
    % configuration
    verbose = 0;
    Z_MIN = 0;
    Z_MAX = thickness;  % 10

    objOutputName = sprintf('%s\\skeleton.obj', imageOutputFolder);
%     binaryImage = imread(imageName);

    if verbose
        figure; imagesc(binaryImage); colormap(gray); axis image; title('skeleton original');
    end

    % faster: use a smaller image
%     binaryImage = binaryImage(150:250, 70:250); % <--- for a.png
%     binaryImage = binaryImage(200:250, 130:230); % <--- for a.png
%     binaryImage = binaryImage(200:230, 200:230); % <--- for a.png
%     binaryImage = binaryImage(:, 3:18); % <--- for binsm.png
%     if verbose
%         figure; imagesc(binaryImage); colormap(gray); axis image; title('skeleton cutted');
%     end

    binaryImage = padarray(binaryImage,[PADSIZE,PADSIZE]);

    if verbose
        figure; imagesc(binaryImage); colormap(gray); axis image; title('skeleton padded');
    end

    %{
    B = bwboundaries(~binaryImage);
    if verbose
        figure; imagesc(binaryImage); colormap(gray); hold on;
        for i=1:length(B)
            plot(B{i,1}(:,2),B{i,1}(:,1),'.','MarkerSize',4);
        end
        hold off;
        axis image; title(length(B));
    end
    %}



    % full triangulation
    %{
    dt = delaunayTriangulation(x, y);
    % v = dt.Points;
    if verbose
        figure; imagesc(binaryImage); colormap(gray); hold on;
        plot(v(:,1),v(:,2),'.','MarkerSize',18);
        for i=1:size(dt.ConnectivityList)
            tri = dt.ConnectivityList(i,:);
            plot([v(tri(1),1) v(tri(2),1)],[v(tri(1),2) v(tri(2),2)],'-');
            plot([v(tri(2),1) v(tri(3),1)],[v(tri(2),2) v(tri(3),2)],'-');
            plot([v(tri(3),1) v(tri(1),1)],[v(tri(3),2) v(tri(1),2)],'-');
        end
        axis image; title('pts');
    end
    %}

    binaryImageH = size(binaryImage, 1);
    binaryImageW = size(binaryImage, 2);
    binaryImageSURFACE = binaryImageW*binaryImageH;
    
    % get black (skeleton) pixels => v
    inds = find(~binaryImage);
    [y,x] = ind2sub(size(binaryImage),inds);
    v = [x, y];    

    % skeleton triangulation
    % define triangles of black area for the following cases of any 2 x 2 kernel (p1,p2,p3,p4):
    % 1. kernel black pixels = 4 => define 2 triangles (p1,p2,p3) and (p3,p4,p1)
    % 2. kernel black pixels = 3 => define 1 triangle with them
    % (p1,p2,p3)/(p1,p2,p4)/(p1,p3,p4)/(p2,p3,p4)
    VerticesArray_Total = zeros(binaryImageSURFACE*10, 3); %[]; % (y, x, z): (n x 3)
    VerticesArray_Total_Count = 0;
    ConnectivityList = zeros(binaryImageSURFACE*10, 3); %[]; % (m x 3)
    ConnectivityList_Count = 0;
    fprintf('Skeleton triangulation. Please wait...\n');
    for px=1:binaryImageW-1
        if mod(px,10) == 0
            fprintf('Skeleton triangulation column %d/%d (%.1f%%)\n', ...
                    px, binaryImageW-1, double(px)/double(binaryImageW-1)*100);
        end
        for py=1:binaryImageH-1
            % get points p1-p4 from top-left and clockwise (y, x)
            p1 = [py, px];
            p2 = [py, px+1];
            p3 = [py+1, px+1];
            p4 = [py+1, px];
            kernelSum = binaryImage(p1(1), p1(2)) + binaryImage(p2(1), p2(2)) + ...
                            binaryImage(p3(1), p3(2)) + binaryImage(p4(1), p4(2));
            if kernelSum == 0  % kernel black (0) pixels = 4 => add triangles (p1,p2,p3) and (p3,p4,p1)
                % add triangle (p1,p2,p3)
                [VerticesArray_Total, VerticesArray_Total_Count, ConnectivityList, ConnectivityList_Count] = ...
                    AddHorizontalTriangleBottomUp(p1, p2, p3, VerticesArray_Total, VerticesArray_Total_Count, ConnectivityList, ConnectivityList_Count, Z_MIN, Z_MAX, binaryImage);                
                % add triangle (p3,p4,p1) bottom
                [VerticesArray_Total, VerticesArray_Total_Count, ConnectivityList, ConnectivityList_Count] = ...
                    AddHorizontalTriangleBottomUp(p3, p4, p1, VerticesArray_Total, VerticesArray_Total_Count, ConnectivityList, ConnectivityList_Count, Z_MIN, Z_MAX, binaryImage);                 
            elseif kernelSum == 1  % kernel black (0) pixels = 3
                if binaryImage(p1(1), p1(2)) == 1 % p1 is white => add triangle (p2,p3,p4)
                    [VerticesArray_Total, VerticesArray_Total_Count, ConnectivityList, ConnectivityList_Count] = ...
                        AddHorizontalTriangleBottomUp(p2, p3, p4, VerticesArray_Total, VerticesArray_Total_Count, ConnectivityList, ConnectivityList_Count, Z_MIN, Z_MAX, binaryImage);                     
                elseif binaryImage(p2(1), p2(2)) == 1 % p2 is white => add triangle (p1,p3,p4)
                    [VerticesArray_Total, VerticesArray_Total_Count, ConnectivityList, ConnectivityList_Count] = ...
                        AddHorizontalTriangleBottomUp(p1, p3, p4, VerticesArray_Total, VerticesArray_Total_Count, ConnectivityList, ConnectivityList_Count, Z_MIN, Z_MAX, binaryImage);                                         
                elseif binaryImage(p3(1), p3(2)) == 1 % p3 is white => add triangle (p1,p2,p4)
                    [VerticesArray_Total, VerticesArray_Total_Count, ConnectivityList, ConnectivityList_Count] = ...
                        AddHorizontalTriangleBottomUp(p1, p2, p4, VerticesArray_Total, VerticesArray_Total_Count, ConnectivityList, ConnectivityList_Count, Z_MIN, Z_MAX, binaryImage);                                         
                else % p4 is white => add triangle (p1,p2,p3)
                    [VerticesArray_Total, VerticesArray_Total_Count, ConnectivityList, ConnectivityList_Count] = ...
                        AddHorizontalTriangleBottomUp(p1, p2, p3, VerticesArray_Total, VerticesArray_Total_Count, ConnectivityList, ConnectivityList_Count, Z_MIN, Z_MAX, binaryImage);                                         
                end
            end
        end
    end
   
    if verbose && false
        figure; hold on;
        for i=1:size(ConnectivityList, 1)
            if mod(i,1000) == 0
                fprintf('plot 3D triangles of ConnectivityList %d/%d (%.1f%%)\n', ...
                    i, size(ConnectivityList, 1), double(i)/double(size(ConnectivityList, 1))*100);
            end
            p1 = VerticesArray_Total(ConnectivityList(i,1), :);
            p2 = VerticesArray_Total(ConnectivityList(i,2), :);
            p3 = VerticesArray_Total(ConnectivityList(i,3), :);

            plot3([p1(2), p2(2)],[p1(1), p2(1)],[p1(3), p2(3)],'b-');
            plot3([p2(2), p3(2)],[p2(1), p3(1)],[p2(3), p3(3)],'b-');
            plot3([p3(2), p1(2)],[p3(1), p1(1)],[p3(3), p1(3)],'b-');            

        end
        axis image; title('3D triangles of ConnectivityList');
    end    

    % collect pixels that are on the outline/border between white and black areas
    % => Those that are black and bordered by at least 1 white =>
    % outlineBorderPoints (x, y)
    outlineBorderPoints = [];
    for i=1:size(v, 1)
        x = v(i, 1);
        y = v(i, 2);
        outline = 0;
        for dx=x-1:x+1
            for dy=y-1:y+1
                if dx >=1 && dx <= binaryImageW && dy >= 1 && dy <= binaryImageH % inside image
                    distance = norm([x y] - [dx dy]);
                    if binaryImage(dy, dx) == 1 && distance == 1 % white pixel and cross neighbor
                        outline = 1;
                        break;
                    end 
                end
            end
            if outline
                break;
            end
        end
        if outline
            outlineBorderPoints = [outlineBorderPoints;v(i,:)];
        end
    end
    if verbose && false 
        figure; imagesc(binaryImage); colormap(gray); hold on;
        plot(outlineBorderPoints(:,1),outlineBorderPoints(:,2),'g.','MarkerSize',8);
        axis image; title('outlineBorderPoints before fix');
    end
   
    % fill outlineBorderPoints also with all peripheral points (1st and
    % last rows and columns) so as to triangulate them to in 3D
    % reconstruction
    % just for test
%     outlineBorderPoints = [];
    for i=1:binaryImageW
        p_up = [i, 1];
        if ~pointBelongsToVector(p_up, outlineBorderPoints)
            outlineBorderPoints = [outlineBorderPoints; p_up];
        end
        p_bottom = [i, binaryImageH];
        if ~pointBelongsToVector(p_bottom, outlineBorderPoints)
            outlineBorderPoints = [outlineBorderPoints; p_bottom];
        end
    end  
    for i=1:binaryImageH
        p_left = [1, i];
        if ~pointBelongsToVector(p_left, outlineBorderPoints)
            outlineBorderPoints = [outlineBorderPoints; p_left];
        end
        p_right = [binaryImageW, i];
        if ~pointBelongsToVector(p_right, outlineBorderPoints)
            outlineBorderPoints = [outlineBorderPoints; p_right];
        end
    end     
    if verbose
        figure; imagesc(binaryImage); colormap(gray); hold on;
        plot(outlineBorderPoints(:,1),outlineBorderPoints(:,2),'b.','MarkerSize',8);
        axis image; title('outlineBorderPoints after fix of peripheral');
    end    

    % peripheral points triangulation
    % convert 2D outlineBorderPoints to 3D outlineBorderPoints3D_bottom (z=Z_MIN) and outlineBorderPoints3D_up (z=Z_MAX)
    outlineBorderPointsSize = size(outlineBorderPoints,1);
    outlineBorderPoints3D_bottom = zeros(outlineBorderPointsSize,3);
    outlineBorderPoints3D_up = zeros(outlineBorderPointsSize,3);
    for i=1:outlineBorderPointsSize
        outlineBorderPoints3D_bottom(i,1) = outlineBorderPoints(i,1);
        outlineBorderPoints3D_bottom(i,2) = outlineBorderPoints(i,2);
        outlineBorderPoints3D_bottom(i,3) = Z_MIN;
        outlineBorderPoints3D_up(i,1) = outlineBorderPoints(i,1);
        outlineBorderPoints3D_up(i,2) = outlineBorderPoints(i,2);
        outlineBorderPoints3D_up(i,3) = Z_MAX;    
    end

    % plot outlineBorderPoints3D_bottom, outlineBorderPoints3D_up
    if verbose && false
        figure; hold on;
        plot3(outlineBorderPoints3D_bottom(:,1), outlineBorderPoints3D_bottom(:,2), outlineBorderPoints3D_bottom(:,3),'r.');
        plot3(outlineBorderPoints3D_up(:,1), outlineBorderPoints3D_up(:,2), outlineBorderPoints3D_up(:,3),'g.');
%         axis image; 
        title('outlineBorderPoints3D bottom,up');
    end

    % each peripheral point up (p) must define 2 triangles with each of its neighbors (pn)
    % triangle 1 vertices: p, pn_bottom, p_bottom
    % triangle 2 vertices: p, pn, pn_bottom
    outlineBorderPointsVisited = zeros(size(outlineBorderPoints,1), 1);
    for i=1:outlineBorderPointsSize % each peripheral point up
        outlineBorderPointsVisited(i) = 1;
        if mod(i,100) == 0
            fprintf('triangulating peripheral points %d/%d (%.1f%%)\n', ...
                i, outlineBorderPointsSize, double(i)/double(outlineBorderPointsSize)*100);            
        end
        % (y,x,z)
        p = [outlineBorderPoints3D_up(i,2), outlineBorderPoints3D_up(i,1), outlineBorderPoints3D_up(i,3)];
        p_bottom = [outlineBorderPoints3D_bottom(i,2), outlineBorderPoints3D_bottom(i,1), outlineBorderPoints3D_bottom(i,3)];
        % get neighbors (0-8)
        pNeighborsArray = []; % (y,x,z)
        pCrossNeighborsArray = []; % (y,x,z)
        for j=1:outlineBorderPointsSize % each peripheral point
            % avoid already visited points
            if outlineBorderPointsVisited(j) == 1
                continue;
            end
            p1 = [outlineBorderPoints3D_up(j,2), outlineBorderPoints3D_up(j,1), outlineBorderPoints3D_up(j,3)];
            dist = norm(p-p1);
            if dist == 0 || dist >= 2 % keep 8-connectivity neighbors
                continue;
            end
            % reject diagonal neighbors in case there is a gamma orthogonal connection
            if dist > 1 % p1 diagonal neighbor of p (y,x,z)
                % get diagonal direction (N-north, S-south, E-east, W-west)
                if (p(2)>p1(2) && p(1)>p1(1)) || (p(2)<p1(2) && p(1)<p1(1)) % SW to NE diagonal
                    pointForGammaConnection1 = [max(p(2),p1(2)), min(p(1),p1(1)), p(3)]; % (max(x1,x2), min(y1,y2), z)
                    pointForGammaConnection2 = [min(p(2),p1(2)), max(p(1),p1(1)), p(3)]; % (min(x1,x2), max(y1,y2), z)
                else % NW to SE diagonal
                    pointForGammaConnection1 = [min(p(2),p1(2)), min(p(1),p1(1)), p(3)]; % (min(x1,x2), min(y1,y2), z)
                    pointForGammaConnection2 = [max(p(2),p1(2)), max(p(1),p1(1)), p(3)]; % (max(x1,x2), max(y1,y2), z)                    
                end
                if point3BelongsToVector3(pointForGammaConnection1, outlineBorderPoints3D_up) || ...
                        point3BelongsToVector3(pointForGammaConnection2, outlineBorderPoints3D_up)
                    continue;
                end                
            end
            
            % inform pNeighborsArray, pCrossNeighborsArray 
            pNeighborsArray = [pNeighborsArray; p1];
            if dist == 1    
                pCrossNeighborsArray = [pCrossNeighborsArray; p1];
            end
        end
        neighborsCnt = size(pNeighborsArray, 1); % [2, 8]
        cross_neighborsCnt = size(pCrossNeighborsArray, 1); % [0, 4]
%         if neighborsCnt == 0
%             fprintf('neighborsCnt = %d cross_neighborsCnt = %d\n', neighborsCnt, cross_neighborsCnt);
%         end
        
        pFinalNeighbors = pNeighborsArray; % (y,x,z)
        % avoid multiple triangles: filtering of neighbors
        % disabled (covered by above rule: reject diagonal neighbors in
        % case there is a gamma orthogonal connection)
        %{
        if neighborsCnt == 2 
            if cross_neighborsCnt == 1
                dist = norm(pNeighborsArray(1,:)-pNeighborsArray(2,:));
                % special case of 2 neighbors: one vertical, one diagonal, and
                % being neighbors also => use only vertical neighbor 
                % i.e. p angle with 2 neighbors is 45 degrees
                if dist == 1
                    pFinalNeighbors = pCrossNeighborsArray;
                end
            end
        elseif neighborsCnt > 2
            if cross_neighborsCnt >= 2 % use first 2 cross neighbors
                pFinalNeighbors = pCrossNeighborsArray(1:2, :);
            elseif cross_neighborsCnt == 1 % use cross neighbor and first diagonal neighbor
                pFinalNeighbors = pCrossNeighborsArray;
                pFinalNeighbors = [pFinalNeighbors; pFinalNeighbors(1, :)];
            else % use first 2 diagonal neighbors
                pFinalNeighbors = pFinalNeighbors(1:2, :); 
            end
        end  
        %}

        % define triangles
        final_neighborsCnt = size(pFinalNeighbors, 1);
%         if final_neighborsCnt == 0
%             fprintf('final_neighborsCnt = %d at (%d, %d)\n', final_neighborsCnt, p(2), p(1));
%         end
        for j=1:final_neighborsCnt % for each peripheral neighbor (pn)
            pn = pFinalNeighbors(j,:);
            pn_bottom = pn;
            pn_bottom(3) = Z_MIN;
            % define 2 triangles with each of its neighbors (pn)
            % triangle 1 vertices: p, pn_bottom, p_bottom
            % triangle 2 vertices: p, pn, pn_bottom                
            [VerticesArray_Total, VerticesArray_Total_Count, ConnectivityList, ConnectivityList_Count] = ...
                AddVertical3DTriangle(p_bottom, pn_bottom, p, VerticesArray_Total, VerticesArray_Total_Count, ConnectivityList, ConnectivityList_Count, Z_MIN, Z_MAX, binaryImage);
            [VerticesArray_Total, VerticesArray_Total_Count, ConnectivityList, ConnectivityList_Count] = ...
                AddVertical3DTriangle(pn_bottom, pn, p, VerticesArray_Total, VerticesArray_Total_Count, ConnectivityList, ConnectivityList_Count, Z_MIN, Z_MAX, binaryImage);                       
        end
    end
    
    % keep needed elements of VerticesArray_Total and ConnectivityList
    VerticesArray_Total = VerticesArray_Total(1:VerticesArray_Total_Count, :);
    ConnectivityList = ConnectivityList(1:ConnectivityList_Count, :);
    
    % plot 3D total results   
    if verbose && false 
        figure; hold on;
        for i=1:size(ConnectivityList, 1)
            if mod(i,1000) == 0
                fprintf('plot 3D triangles of ConnectivityList %d/%d (%.1f%%)\n', ...
                    i, size(ConnectivityList, 1), double(i)/double(size(ConnectivityList, 1))*100);
            end
            p1 = VerticesArray_Total(ConnectivityList(i,1), :);
            p2 = VerticesArray_Total(ConnectivityList(i,2), :);
            p3 = VerticesArray_Total(ConnectivityList(i,3), :);

            plot3([p1(2), p2(2)],[p1(1), p2(1)],[p1(3), p2(3)],'b-');
            plot3([p2(2), p3(2)],[p2(1), p3(1)],[p2(3), p3(3)],'b-');
            plot3([p3(2), p1(2)],[p3(1), p1(1)],[p3(3), p1(3)],'b-');            

        end
        axis image; title('3D triangles of ConnectivityList');
    end         
    
    % swap VerticesArray_Total 1st with 2nd column => VerticesArray_Total (x,y,z)
    c1 = VerticesArray_Total(:,1);
    c2 = VerticesArray_Total(:,2);
    c3 = VerticesArray_Total(:,3);
    VerticesArray_Total = [c2, c1, c3];   
    
    % create normals
    TR = triangulation(ConnectivityList, VerticesArray_Total);
    VerticesNormalsArray_Total = vertexNormal(TR);    
    % Plot the triangulated surface and the unit normal vectors.
    if verbose && false
        figure;
        trisurf(TR,'FaceColor',[0.8 0.8 1.0]);
        axis equal
        hold on
        quiver3(VerticesArray_Total(:,1),VerticesArray_Total(:,2),VerticesArray_Total(:,3), ...
             VerticesNormalsArray_Total(:,1),VerticesNormalsArray_Total(:,2),VerticesNormalsArray_Total(:,3),10.5,'Color','r'); 
        title('VerticesNormalsArray_Total', 'Interpreter', 'none');
    end
    
    % write obj file objOutputName
    fileObjs = fopen(objOutputName,'w');
    % Writing the obj file for the skeleton...
    fprintf(fileObjs, '# Vertices\n');
    fprintf(fileObjs, 'v %f %f %f\n', VerticesArray_Total');
    fprintf(fileObjs, '# Vertex Normals\n');
    fprintf(fileObjs, 'vn %f %f %f\n', VerticesNormalsArray_Total');
    fprintf(fileObjs, '# Faces\n');
    fprintf(fileObjs, 'f %d//%d %d//%d %d//%d\n', [ConnectivityList, ConnectivityList]');
    % e.g. (1,2,3) is written as: 1//2 3//1 2//3
    fclose(fileObjs);    
    
    tilefigs;
    
    timeElapsedSec = toc; % Read the stopwatch timer  
    hms = sec2hms(timeElapsedSec);
    fprintf('GetVitroImage3D_Skeleton(): timeElapsed = %f sec (%s)\n', timeElapsedSec, hms);     
end % runme5skel

%{ 
---------------------------------------------------------------------------
                    pointBelongsToVector()
---------------------------------------------------------------------------
%}
function found = pointBelongsToVector(point, Vector)
    found = false;
    for i=1:size(Vector, 1)
        if point(1) == Vector(i,1) && point(2) == Vector(i,2)
            found = true;
            return;
        end
    end
end

%{ 
---------------------------------------------------------------------------
                    point3BelongsToVector3()
---------------------------------------------------------------------------
%}
function found = point3BelongsToVector3(point, Vector)
    found = false;
    for i=1:size(Vector, 1)
        if point(1) == Vector(i,1) && point(2) == Vector(i,2) && point(3) == Vector(i,3)
            found = true;
            return;
        end
    end
end

%{ 
---------------------------------------------------------------------------
                    AddHorizontalTriangleBottomUp()
---------------------------------------------------------------------------
p1, p2, p3, VerticesArray_Total: (y,x,z)!
---------------------------------------------------------------------------
%}
function [VerticesArray_Total, VerticesArray_Total_Count, ConnectivityList, ConnectivityList_Count] = ...
            AddHorizontalTriangleBottomUp(p1, p2, p3, ...
            VerticesArray_Total, VerticesArray_Total_Count, ConnectivityList, ConnectivityList_Count,...
            Z_MIN, Z_MAX, binaryImage)
        
    % add triangle (p1,p2,p3) bottom
    p1_bottom = [p1, Z_MIN];
    p2_bottom = [p2, Z_MIN];
    p3_bottom = [p3, Z_MIN];
    [VerticesArray_Total, VerticesArray_Total_Count, ConnectivityList, ConnectivityList_Count] = ...
            AddVertical3DTriangle(p1_bottom, p2_bottom, p3_bottom, VerticesArray_Total, VerticesArray_Total_Count, ConnectivityList, ConnectivityList_Count, Z_MIN, Z_MAX, binaryImage);
    % add triangle (p1,p2,p3) up
    p1_up = [p1, Z_MAX];
    p2_up = [p2, Z_MAX];
    p3_up = [p3, Z_MAX];
    [VerticesArray_Total, VerticesArray_Total_Count, ConnectivityList, ConnectivityList_Count] = ...
            AddVertical3DTriangle(p1_up, p2_up, p3_up, VerticesArray_Total, VerticesArray_Total_Count, ConnectivityList, ConnectivityList_Count, Z_MIN, Z_MAX, binaryImage);                        
end

%{ 
---------------------------------------------------------------------------
                    AddVertical3DTriangle()
---------------------------------------------------------------------------
p1, p2, p3, VerticesArray_Total: (y,x,z)!
---------------------------------------------------------------------------
%}
function [VerticesArray_Total, VerticesArray_Total_Count, ConnectivityList, ConnectivityList_Count] = ...
            AddVertical3DTriangle(p1, p2, p3, ...
            VerticesArray_Total, VerticesArray_Total_Count, ConnectivityList, ConnectivityList_Count, ...
            Z_MIN, Z_MAX, binaryImage)
    
    % fix points orientation
    pointsYX = 1;
    [p1, p2, p3] = OrderTriangleTowardsLightSide(p1, p2, p3, Z_MIN, Z_MAX, binaryImage, pointsYX);
        
    % add triangle (p1,p2,p3) 
    VerticesArray_Total_Count = VerticesArray_Total_Count + 1;
    VerticesArray_Total(VerticesArray_Total_Count,:) = p1;  
    VerticesArray_Total_Count = VerticesArray_Total_Count + 1;
    VerticesArray_Total(VerticesArray_Total_Count,:) = p2; 
    VerticesArray_Total_Count = VerticesArray_Total_Count + 1;
    VerticesArray_Total(VerticesArray_Total_Count,:) = p3;
    connectivity = [VerticesArray_Total_Count-2, VerticesArray_Total_Count-1, VerticesArray_Total_Count];
    ConnectivityList_Count = ConnectivityList_Count + 1;
    ConnectivityList(ConnectivityList_Count,:) = connectivity;   
    
    % test to add triangle twice with both orders: clockwise & counterclockwise
    % to change order just swap 1st with 3rd point
    % add triangle (p3,p2,p1) => X
    %{
    connectivity = [VerticesArray_Total_Count, VerticesArray_Total_Count-1, VerticesArray_Total_Count-2];
    ConnectivityList_Count = ConnectivityList_Count + 1;
    ConnectivityList(ConnectivityList_Count,:) = connectivity;    
    %}
end





