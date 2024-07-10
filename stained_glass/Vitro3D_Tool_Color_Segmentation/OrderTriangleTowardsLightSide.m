%{ 
---------------------------------------------------------------------------
                    OrderTriangleTowardsLightSide()
---------------------------------------------------------------------------
%}
function [p1, p2, p3] = OrderTriangleTowardsLightSide(p1, p2, p3, Z_MIN, Z_MAX, binaryImage, pointsYX)
    if pointsYX % invert from (y,x) to (x,y)
        p1 = pointInvertXY_coordinates(p1);
        p2 = pointInvertXY_coordinates(p2);
        p3 = pointInvertXY_coordinates(p3);        
    end

    V = GetTriangleVertexNormal(p1, p2, p3);

    % V direction is ALWAYS towards to you and points 1,2,3 are in
    % counterclockwise order (right hand rule)
    if p1(3) == Z_MAX && p2(3) == Z_MAX && p3(3) == Z_MAX % 1. triangle horizontal (same z) up (z = Z_MAX)
        if V(1,3) == -1 % vector points down and should point up => change order
            % reorder points by swaping p1, p3
            [p1, p3] = swapPoints(p1, p3);

        end
    elseif p1(3) == Z_MIN && p2(3) == Z_MIN && p3(3) == Z_MIN % 2. triangle horizontal (same z) bottom (z = Z_MIN)          
        if V(1,3) == 1 % vector points up and should point down => change order
            % reorder points by swaping p1, p3
            [p1, p3] = swapPoints(p1, p3);
        end   
    else % triangle vertical: 2 points with same z (the 3rd with has always the same (x,y) with one of the rest)
        % get 2 check points with same z => chekPoint1, chekPoint2
        if p1(3) == p2(3)
            chekPoint1 = p1;
            chekPoint2 = p2;
        elseif p1(3) == p3(3)
            chekPoint1 = p1;
            chekPoint2 = p3;            
        else
            chekPoint1 = p2;
            chekPoint2 = p3;            
        end
        
        % move check points by V to get their vertical neighbors
        chekPoint1_neighbor = int32(chekPoint1 + V(1,:));
        chekPoint2_neighbor = int32(chekPoint2 + V(1,:));
        
        % debug
%         chekPoint1_neighbor = double(chekPoint1_neighbor);
%         chekPoint2_neighbor = double(chekPoint2_neighbor);
%         d1 = norm(chekPoint1_neighbor - chekPoint1);
%         d2 = norm(chekPoint2_neighbor - chekPoint2);
%         if (d1 > 1.42 || d2 > 1.42)
%             here = 1;
%         end
        
        binaryImageH = size(binaryImage, 1);
        binaryImageW = size(binaryImage, 2);        
        
        % check from binaryImage check points neighbors if they are black(dark) 
        % => reorder points
        point1InImage = pointInImage(chekPoint1_neighbor, binaryImageW, binaryImageH);
        point2InImage = pointInImage(chekPoint2_neighbor, binaryImageW, binaryImageH);       
        if (point1InImage && binaryImage(chekPoint1_neighbor(2), chekPoint1_neighbor(1)) == 0) || ...
           (point2InImage && binaryImage(chekPoint2_neighbor(2), chekPoint2_neighbor(1)) == 0)
            % reorder points by swaping p1, p3
            [p1, p3] = swapPoints(p1, p3);
            
            % bug fix: case of both points in image but with different values
            % in binaryImage => do not reorder (cancel previous reorder)
            % case of corner points (acute angle) 
            if (point1InImage && point2InImage) && ...
               (binaryImage(chekPoint1_neighbor(2), chekPoint1_neighbor(1)) ~= binaryImage(chekPoint2_neighbor(2), chekPoint2_neighbor(1)))
                % reorder points by swaping p1, p3
                [p1, p3] = swapPoints(p1, p3);
            end
        
        end
         
    end 
    
    % inverse order of ALL triangles
    % maybe MeshLab and Matlab have opposite convention
    % if it is needed, add a new parameter:
    % OrderTriangleTowardsDarkSide (1/0) and do the following if OrderTriangleTowardsDarkSide
    [p1, p3] = swapPoints(p1, p3);
    
    if pointsYX % invert from (x,y) back to (y,x)
        p1 = pointInvertXY_coordinates(p1);
        p2 = pointInvertXY_coordinates(p2);
        p3 = pointInvertXY_coordinates(p3);        
    end    
end

%{ 
---------------------------------------------------------------------------
                    pointInvertXY_coordinates()
---------------------------------------------------------------------------
%}
function p_inv = pointInvertXY_coordinates(p)
    p_inv = [p(2), p(1), p(3)];
end

%{ 
---------------------------------------------------------------------------
                    pointInImage()
---------------------------------------------------------------------------
%}
function inImage = pointInImage(p, imageW, imageH)
    % x in [1,W] and y in [1,H]
    inImage = p(1) >= 1 && p(1) <= imageW && p(2) >= 1 && p(2) <= imageH;
end

%{ 
---------------------------------------------------------------------------
                    swapPoints()
---------------------------------------------------------------------------
%}
function [p1, p2] = swapPoints(p1, p2)
    tmp = p1;
    p1 = p2;
    p2 = tmp;
end

%{ 
---------------------------------------------------------------------------
                    GetTriangleVertexNormal()
---------------------------------------------------------------------------
todo? for acceleration:
Given 3 points A,B,C. Take the cross product AB×AC. This gives you the normal vector
---------------------------------------------------------------------------
%}
function V = GetTriangleVertexNormal(p1, p2, p3)
    P = [p1;p2;p3]; 
    TR = triangulation([1, 2, 3], P);
    V = vertexNormal(TR);
%     plotTriangle(p1, p2, p3, TR, P, V);
end

%{ 
---------------------------------------------------------------------------
                    plotTriangle()
---------------------------------------------------------------------------
%}
function plotTriangle(p1, p2, p3, TR, P, V)
    % Plot the triangulated surface and the unit normal vectors.
    figure;
    trisurf(TR,'FaceColor',[0.8 0.8 1.0]);
    axis equal
    hold on
    plot3(p1(1), p1(2), p1(3), 'ro');
    text(p1(1), p1(2), p1(3), '1');
    plot3(p2(1), p2(2), p2(3), 'go');
    text(p2(1), p2(2), p2(3), '2');
    plot3(p3(1), p3(2), p3(3), 'bo');  
    text(p3(1), p3(2), p3(3), '3');

    quiver3(P(:,1),P(:,2),P(:,3), ...
         V(:,1),V(:,2),V(:,3),0.5,'Color','b');
    title('plotTriangle()', 'Interpreter', 'none');    
end



