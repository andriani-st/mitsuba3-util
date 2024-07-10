function sortedPointsArray = sortPointsClockwise(PointsArray, do_debug, vSettings)

if ~exist('do_debug','var')
    do_debug = 0;
end

% npts = 1000;
if size(PointsArray, 1) >= 6
    [zg1, zg2, ag, bg, alphag] = fitellipse_mex(PointsArray(:,1),PointsArray(:,2));
    ellipse.z = [zg1, zg2];
    ellipse.a = ag;
    ellipse.b = bg;
    ellipse.alpha = alphag;
%     [ellipse.z, ellipse.a, ellipse.b, ellipse.alpha] = fitellipse(PointsArray);%, 'linear');
    if (~isnan(ellipse.z))
%         ellipsePerimeter = round(2*pi()*sqrt((power(ellipse.a,2)+power(ellipse.b,2))/2));
        ellipsePoints = getEllipsePoints(ellipse.z, ellipse.a, ellipse.b, ellipse.alpha, 1000);%2*ellipsePerimeter); % clockwise from 12 o'clock
%         ellipsePoints = getEllipsePoints(ellipse.z, ellipse.a, ellipse.b, ellipse.alpha, npts); % clockwise from 12 o'clock
        dropletCenter = [mean(ellipsePoints(:,1)), mean(ellipsePoints(:,2))];
    else
        dropletCenter = [mean(PointsArray(:,1)), mean(PointsArray(:,2))];
    end
else
    dropletCenter = [mean(PointsArray(:,1)), mean(PointsArray(:,2))];
end

A = PointsArray(:, 1) - dropletCenter(1);
B = PointsArray(:, 2) - dropletCenter(2);
thetas = atan2d(B, A);

% convert thetas from [-180, 180] to [0, 360] => clockwise with 0 at 3 o'clock
for i=1:size(thetas, 1)
    if thetas(i) < 0
        thetas(i) = 360 + thetas(i);
    end
end

PointsArrayAndThetas = [PointsArray, thetas];
PointsArrayAndThetasSorted = sortrows(PointsArrayAndThetas, 3);

% start from 1st point with angle > 90 (after 6 o'clock) clockwise
pointsAfter6oclockIndeces = find(PointsArrayAndThetasSorted(:, 3) > 90);
if isempty(pointsAfter6oclockIndeces)
    firstPointIndx = 1;
else
    firstPointIndx = pointsAfter6oclockIndeces(1);
end

%     sortedPointsArray = PointsArrayAndThetasSorted(:, 1:2);
sortedPointsArray = PointsArrayAndThetasSorted(firstPointIndx:end, 1:2);
sortedPointsArray = [sortedPointsArray; PointsArrayAndThetasSorted(1:firstPointIndx-1, 1:2)];

%     [x2, y2] = poly2cw(PointsArray(:, 1), PointsArray(:, 2));
%     sortedPointsArray = [x2, y2];

if do_debug
    
    figure;
    imagesc(vSettings.I); colormap(gray); axis image;
    hold on;
    plot(PointsArray(:,1), PointsArray(:,2), '.r');
    plot(sortedPointsArray(:,1), sortedPointsArray(:,2), 'og');
    
    for i=1:size(sortedPointsArray,1)
        text(sortedPointsArray(i,1), sortedPointsArray(i,2), sprintf(' %d',i),'BackgroundColor',[1 1 1]);
    end
    axis equal
end

end % function