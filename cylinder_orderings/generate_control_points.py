import numpy as np
import mpmath
import math

r1 = 0.07
r2 = 0.03
r3 = 0.05
r4 = 0.02

level_dist = [0.2, 0.2, 0.2, 0.5]

m = 10

r = [r1, r2, r3, r4]
R = []
for i in r:
    R.append(i*mpmath.csc(math.pi/m))

deg_i = 360 / m
deg = []
for i in range(0,m):
    deg.append(i*deg_i)

f = open("curves.txt", "w")

for i in deg:
    for j in range(0,len(R)):
        f.write(str(np.sin(math.radians(i))*R[j]) + " " + str(j*level_dist[j]) + " " + str(np.cos(math.radians(i))*R[j]) + " " + str(r[j]) + "\n")
        print(np.sin(math.radians(i))*R[j], j*level_dist[j], np.cos(math.radians(i))*R[j], r[j])
    print()
    f.write("\n")

f.close()

