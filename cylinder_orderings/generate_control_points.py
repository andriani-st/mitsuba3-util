import numpy as np
import mpmath
import math

#f = open("demofile2.txt", "a")
#.write("Now the file has more content!")
#f.close()

r1 = 0.07
r2 = 0.03
r3 = 0.05
r4 = 0.05
m = 10
R1 = r1*mpmath.csc(math.pi/m)
R2 = r2*mpmath.csc(math.pi/m)
R3 = r3*mpmath.csc(math.pi/m)
R4 = r4*mpmath.csc(math.pi/m)

deg = [0,36,36*2,36*3,36*4,36*5,36*6,36*7,36*8,36*9]
print(R1)
for i in deg:
    print(np.sin(math.radians(i))*R1, 0.0, np.cos(math.radians(i))*R1, r1)
    print(np.sin(math.radians(i))*R2, 0.3, np.cos(math.radians(i))*R2, r2)
    print(np.sin(math.radians(i))*R3, 0.5, np.cos(math.radians(i))*R3, r3)
    print(np.sin(math.radians(i))*R4, 0.6, np.cos(math.radians(i))*R4, r4)
    print()
    #print("z=",np.cos(math.radians(36))*R)
