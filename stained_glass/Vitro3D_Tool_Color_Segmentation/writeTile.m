function writeTile(tileFilename,vertices,vertex_normals,faces)
fileObj = fopen(tileFilename,'w');
fprintf(fileObj, '# Vertices\n');
fprintf(fileObj, 'v %f %f %f\n', vertices');
fprintf(fileObj, '# Vertex Normals\n');
fprintf(fileObj, 'vn %f %f %f\n', vertex_normals');
fprintf(fileObj, '# Faces\n');
fprintf(fileObj, 'f %d//%d %d//%d %d//%d\n', [faces, faces]');
fclose(fileObj);
end % function