%{ 
---------------------------------------------------------------------------
                    test_OrderTriangleTowardsLightSide()
---------------------------------------------------------------------------
%}
function test_OrderTriangleTowardsLightSide()
    close all; clear; clc;
    
%     p1 = [rand(), rand(), rand()];
%     p2 = [rand(), rand(), rand()];
%     p3 = [rand(), rand(), rand()];

    Z_MIN = 0;
    Z_MAX = 30;
    PADSIZE = 10;
    binaryImage = imread('a.png');
    binaryImage = padarray(binaryImage,[PADSIZE,PADSIZE]);
    
    p1 = [1, 1, Z_MAX];
    p2 = [2, 1, Z_MAX];
    p3 = [2, 2, Z_MAX];    
    [p1, p2, p3] = OrderTriangleTowardsLightSide(p1, p2, p3, Z_MIN, Z_MAX, binaryImage, 1);
    return;
    
    % 1. triangle horizontal (same z) up (z = Z_MAX)
    p1 = [10, 20, Z_MAX];
    p2 = [11, 20, Z_MAX];
    p3 = [11, 21, Z_MAX];    
    [p1, p2, p3] = OrderTriangleTowardsLightSide(p1, p2, p3, Z_MIN, Z_MAX, binaryImage, 0);
    
    % 2. triangle horizontal (same z) bottom (z = Z_MIN)
    p1 = [10, 20, Z_MIN];
    p2 = [11, 20, Z_MIN];
    p3 = [11, 21, Z_MIN];
    [p1, p2, p3] = OrderTriangleTowardsLightSide(p1, p2, p3, Z_MIN, Z_MAX, binaryImage, 0);
    % 3. triangle vertical and 2 points with same z, vertical: with same x
    p1 = [20, 22, Z_MAX];
    p2 = [20, 21, Z_MAX]; 
    p3 = [20, 22, Z_MIN];
    [p1, p2, p3] = OrderTriangleTowardsLightSide(p1, p2, p3, Z_MIN, Z_MAX, binaryImage, 0);
    % 4. triangle vertical and 2 points with same z, horizontal: with same y
    p1 = [21, 20, Z_MAX];
    p2 = [22, 20, Z_MAX]; 
    p3 = [21, 20, Z_MIN];
    [p1, p2, p3] = OrderTriangleTowardsLightSide(p1, p2, p3, Z_MIN, Z_MAX, binaryImage, 0);
    % 5. triangle vertical and 2 points with same z, diagonal: top-right to bottom-left e.g. (1,1), (2,2)
    p1 = [20, 20, Z_MAX];
    p2 = [21, 21, Z_MAX]; 
    p3 = [20, 20, Z_MIN];
    [p1, p2, p3] = OrderTriangleTowardsLightSide(p1, p2, p3, Z_MIN, Z_MAX, binaryImage, 0);
    % 6. triangle vertical and 2 points with same z, diagonal: top-left to bottom-right e.g. (1,2), (2,1)
    p1 = [20, 21, Z_MAX];
    p2 = [21, 20, Z_MAX]; 
    p3 = [20, 21, Z_MIN];
    [p1, p2, p3] = OrderTriangleTowardsLightSide(p1, p2, p3, Z_MIN, Z_MAX, binaryImage, 0);
    
  tilefigs;
    

end