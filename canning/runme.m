format compact;
close all; clear; clc;
N = 100;
ncanes = 40;
maxTwist = 60;
angles = deg2rad(linspace(0,360,ncanes));
anglesTwist = deg2rad(linspace(0,maxTwist,N));

pts = [0 0; -.5 .5;  -1 1;  -1 2; -.5 3]'; % mporw na parw tis sintetagmenes tou profil enos symmetrikou antikeimenou (px apo to paint) na ta valw edw kai tha mou ftiaksei to antikeimeno!!!
xpts = interp1(1:size(pts,2),pts(1,:),linspace(1,size(pts,2),N),'spline');
ypts = interp1(1:size(pts,2),pts(2,:),linspace(1,size(pts,2),N),'spline');

pts3D = zeros(3,N);
pts3D(1,:) = xpts;
pts3D(3,:) = ypts;

figure; hold on;
plot(pts(1,:),pts(2,:),'-');
plot(xpts,ypts,'.');
hold off; axis equal;

figure; 
plot3(pts3D(1,:),pts3D(2,:),pts3D(3,:),'.')
axis equal; view(3); rotate3d('on');
xlabel x; ylabel y; zlabel z;


pts4D = zeros(3,N,ncanes);
for i=1:ncanes
    local_pts = Rz(angles(i))*pts3D;
    pts4D(:,:,i) = local_pts;
end

figure; hold on
for i=1:ncanes
    plot3(pts4D(1,:,i),pts4D(2,:,i),pts4D(3,:,i),'.')    
end
hold off; axis equal; view(3); rotate3d('on');
xlabel x; ylabel y; zlabel z;

pts4Dtwist = zeros(size(pts4D));
for i=1:N
    local_pts = Rz(anglesTwist(i))*squeeze(pts4D(:,i,:));
    pts4Dtwist(1,i,:) = local_pts(1,:);
    pts4Dtwist(2,i,:) = local_pts(2,:);
    pts4Dtwist(3,i,:) = local_pts(3,:);
%     figure; hold on;
%     plot3(squeeze(pts4D(1,i,:)),squeeze(pts4D(2,i,:)),squeeze(pts4D(3,i,:)),'.')
%     plot3(squeeze(pts4Dtwist(1,i,:)),squeeze(pts4Dtwist(2,i,:)),squeeze(pts4Dtwist(3,i,:)),'.')
%     view(3);
%     hold off; axis equal
end

figure; hold on
for i=1:ncanes
    plot3(pts4Dtwist(1,:,i),pts4Dtwist(2,:,i),pts4Dtwist(3,:,i),'-','Linewidth',2)    
end
hold off; axis equal; view(3); rotate3d('on');
xlabel x; ylabel y; zlabel z;

fileID1 = fopen('curves_twist_1.txt','w');
fileID2 = fopen('curves_twist_2.txt','w');
for i=1:2:ncanes
    for j=1:100
        fprintf(fileID1,'%.4f %4f %4f 0.03\n',pts4Dtwist(1,j,i), pts4Dtwist(2,j,i), pts4Dtwist(3,j,i));
    end
    fprintf(fileID1,'\n');
end

for i=2:2:ncanes
    for j=1:100
        fprintf(fileID2,'%.4f %4f %4f 0.03\n',pts4Dtwist(1,j,i), pts4Dtwist(2,j,i), pts4Dtwist(3,j,i));
    end
    fprintf(fileID2,'\n');
end
