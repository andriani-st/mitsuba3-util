function [binds,newInds] = erodeContour2(imsiz,inds,siz,verbose)
I = zeros(imsiz(1),imsiz(2));
I(inds) = 1;
se = strel('disk', siz);
erodedBW = imerode(I,se);
B = bwboundaries(erodedBW,8,'noholes','pixeledge');

if isempty(B) || length(B)>1
    erodedBW = I;
    B = bwboundaries(I~=0,8,'noholes','pixeledge');
%     disp('using orig')
elseif length(B{1,1}) < 20
    erodedBW = I;
    B = bwboundaries(I~=0,8,'noholes','pixeledge');
%     disp('using orig 2')
end

if verbose
    figure; imagesc(erodedBW); colormap(gray);
    hold on
    plot(B{1,1}(:,2),B{1,1}(:,1),'.b')
    for i=1:length(B{1,1})
        text(B{1,1}(i,2),B{1,1}(i,1),sprintf(' %d',i),'Color',[1 0 0])
    end
    hold off; axis image
end

newInds = find(erodedBW);


se2 = ones(3);%[0 1 0; 1 1 1; 0 1 0]';
BW2 = conv2(erodedBW,se2,'same');

[y,x] = ind2sub(imsiz,newInds);
Xs = zeros(1,length(newInds));
Ys = zeros(1,length(newInds));
binds = zeros(1,length(newInds));
cnt = 0;
for i=1:length(newInds)
    clause1 = (BW2(y(i),x(i)) < 8) && (BW2(y(i),x(i)) > 0); 
    clause2 = BW2(y(i),x(i)) > 0 && (y(i)==1 || x(i)==1);
    if clause1 || clause2
        cnt = cnt + 1;
%         for j=1:length(contourO)
%             if contourO(j,1) == x(i) && contourO(j,2) == y(i)
%                 break;
%             end
%         end
        binds(1,cnt) = i;
        Xs(1,cnt) = x(i);
        Ys(1,cnt) = y(i);
    end
end
binds = binds(1,1:cnt);
Xs = Xs(1,1:cnt);
Ys = Ys(1,1:cnt);

% Points = [x, y];
% [~,binds] = sortIndexPointsClockwise(Points, binds, verbose);

if verbose
    figure; imagesc(BW2.*erodedBW); axis image; impixelinfo
    figure; imagesc(I); colormap(gray);
    axis image; title('original');
    figure; imagesc(erodedBW); colormap(gray); hold on;
    plot(Xs,Ys,'.b');
    hold off; axis image; title('erode');
end

end % function