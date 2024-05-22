function rz = Rz(a)

cosphi = cos(a);
sinphi = sin(a);
rz = [ cosphi -sinphi 0; sinphi cosphi 0; 0 0 1];
