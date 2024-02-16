# mitsuba3-util

This util integrates mitsuba3 and provides a number of options to create rendered images or animations of objects. Also, some more specilised applications were created as described in the README files in stained_glass, filigree and cylinder_orderings folders. 

## Prerequisites
- Python
- mitsuba3 (https://mitsuba.readthedocs.io/en/latest/)
- OpenCV (https://pypi.org/project/opencv-python/)
- MATLAB

## Running the util
To run the util
```
python3 util.py /path/to/json/file/config.json
```

By modifying the config.json that passes as an argument above, the following outputs are available:
- Rendered png images of specified size and quality
- Rotation videos of specified number of views (e.g. full rotations with 360 views)
- Animation videos by rendering OBJ frames provided or by providing translation matrices
- Rotation videos of animations of specified number of views

In more detail:

## Creating an image of specified size and quality
