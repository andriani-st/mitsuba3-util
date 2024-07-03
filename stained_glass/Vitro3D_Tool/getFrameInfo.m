function [framePoints, frameEdges] = getFrameInfo(imageHeight, imageWidth, numPointsPerEdge,verbose)
% Define corner points
corners = [1, 1;                    % Top-left
    imageWidth, 1;           % Top-right
    imageWidth, imageHeight; % Bottom-right
    1, imageHeight];         % Bottom-left

% Generate more points along the edges
x = linspace(1, imageWidth, numPointsPerEdge);
y = linspace(1, imageHeight, numPointsPerEdge);

% Top edge (excluding corners)
top_edge = [x(2:end-1); ones(1, numPointsPerEdge-2)]';

% Bottom edge (excluding corners)
bottom_edge = [x(2:end-1); imageHeight * ones(1, numPointsPerEdge-2)]';

% Left edge (excluding corners)
left_edge = [ones(1, numPointsPerEdge-2); y(2:end-1)]';

% Right edge (excluding corners)
right_edge = [imageWidth * ones(1, numPointsPerEdge-2); y(2:end-1)]';

% Combine all points
framePoints = [corners(1,:); top_edge; corners(2,:); right_edge; corners(3,:); bottom_edge; corners(4,:); left_edge];

% Set frame edges
numPoints = size(framePoints,1);
frameEdges = [(1:numPoints-1)', (2:numPoints)'; numPoints, 1];

% if verbose
%     whos framePoints frameEdges
%     figure; hold on;
%     plot(framePoints(:,1),framePoints(:,2),'.');
%     hold off; axis equal; 
%     frameEdges
% end
end