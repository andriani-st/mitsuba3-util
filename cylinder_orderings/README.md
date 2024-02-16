This util is used to create objects constructed by placing cylinders in circular ordering. To create these objects 
a curves.txt file is required.
This file contains informations for each cylinder/curve. In more detail, for a curve with 3 control points its 
corresponding information in curves.txt will look like:

```
0.0 0.0 0.226524758424985 0.07
0.0 0.3 0.0970820393249937 0.03
0.0 0.5 0.16180339887499 0.05
```

The first 3 values in each row represents the x,y,z coordinates of the control point and the last one the radius of the
cylinder at this point. The user has the option to provide the curves.txt file or run the "generate_control_points.py"
script to create by providing a "curves_requirements.json" file:
```
python3 generate_control_points.py curves_requirements.json
```

The json file must look like:
```
{
  "cylinders_num": 10,
  "control_points": [
    {
      "radius": 0.07,
      "y": 0
    },
    {
      "radius": 0.03,
      "y": 0.3
    },
    {
      "radius": 0.05,
      "y": 0.5
    }
  ]
}
```

Then the glass_cylinders.py script must be executed that takes information automatically from the curves.txt file:
```
python3 glass_cylinders_bend.py
```
The script adds a base of appropriate size for the object and the final rendered image will look something like the following image:
![image](https://github.com/andriani-st/mitsuba3-util/assets/77795248/b477d1ba-77a2-4a2a-9cf7-cda86a6a9363)

