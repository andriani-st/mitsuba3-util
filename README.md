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
- Animation videos by rendering OBJ frames
- Rotation videos of animations of specified number of views

In more detail:

## Creating an image of specified size and quality
A basic configuration file for rendering an object from an OBJ file will look like:
```
{
  "output": {
    "type": "image",
    "spp": 1024,
    "width": 512
    "height": 512
},
"camera": {
  "fov": 45,
},
"objects": [
  {
      "name": "glass",
      "filename": "glass.obj",
      "material": {
         "type": "glass"
      }
  }
],
"lights": [
  {
      "name": "light1",
      "emitter_type": "area",
      "emitter_shape": "rectangle",
      "position": "back"
      "radiance": 10
  }
]
}

```

The above script uses some options provided by the util for the material and the position of the light but the user can also set these values as described in Mitsuba's documentation. The above script created the following rendered image for an object described in glass.obj file:

![image](https://github.com/andriani-st/mitsuba3-util/assets/77795248/5892eada-94a0-4a5f-a945-ed73832e93d7)


## Creating a rotation video
A basic configuration file for creating a rotation video of an OBJ file will look like:

```
{
  "output": {
    "type": "rotation-video",
    "num_views": 360,
    "spp": 1024,
    "width": 512
    "height": 512
},
"camera": {
  "fov": 45,
},
"objects": [
  {
      "name": "glass",
      "filename": "glass.obj",
      "material": {
         "type": "glass"
      }
  }
],
"lights": [
  {
      "name": "light1",
      "emitter_type": "area",
      "emitter_shape": "rectangle",
      "position": "back"
      "radiance": 10
  }
]
}
```

The above configuration file creates a .avi rotation video. Some selected frames of that video:
![image](https://github.com/andriani-st/mitsuba3-util/assets/77795248/a752db2d-b235-4b82-bbf1-ca4382d27a80)
