function res = IsInImage(rp,imageSize)

p = round(rp);

res = ((p(1) > 0) & (p(2) > 0) & (p(1) <= imageSize(2)) & (p(2) <= imageSize(1)));
