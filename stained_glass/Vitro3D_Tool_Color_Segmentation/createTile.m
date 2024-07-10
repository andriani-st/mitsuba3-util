function [vertices,faces,polygonBoundaryPoints] = createTile(tileFilename,points,binds,ConnectivityList,offset,thickness,distortionFactor,verbose)

verticesSurface0 = zeros(3,size(points,1));
verticesSurface1 = zeros(3,size(points,1));
for j=1:size(points,1)
    verticesSurface0(:,j) = [points(j,1), points(j,2),0] + randn(1, 3) * distortionFactor;
    verticesSurface1(:,j) = [points(j,1), points(j,2),thickness] + randn(1, 3) * distortionFactor;
end
vertices = [verticesSurface0 verticesSurface1]';

facesSurface0 = zeros(3,size(ConnectivityList,1));
facesSurface1 = zeros(3,size(ConnectivityList,1));
for j=1:size(ConnectivityList,1)
    facesSurface0(:,j) = [ConnectivityList(j,1), ConnectivityList(j,2), ConnectivityList(j,3)];
    facesSurface1(:,j) = [ConnectivityList(j,3)+offset, ConnectivityList(j,2)+offset, ConnectivityList(j,1)+offset];
end
faces = [facesSurface0 facesSurface1]';
polygonBoundaryPoints = points(binds,:);

if verbose
    figure; hold on;
    plot(points(:,1),points(:,2),'.b');
    plot(polygonBoundaryPoints(:,1),polygonBoundaryPoints(:,2),'or');
    hold off; axis equal;
    title(tileFilename)
end
end % function