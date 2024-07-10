function validTris = findValidTris(dt,dthresh)
bmap = ones(1,size(dt.ConnectivityList,1));
for itri=1:size(dt.ConnectivityList,1)
    tri = dt.ConnectivityList(itri,:);
    il1 = norm(dt.Points(tri(1),:)-dt.Points(tri(2),:));
    il2 = norm(dt.Points(tri(2),:)-dt.Points(tri(3),:));
    il3 = norm(dt.Points(tri(3),:)-dt.Points(tri(1),:));
    if il1>dthresh || il2>dthresh || il3>dthresh
        bmap(1,itri) = 0;
    end
end
validTris = find(bmap);
end % function