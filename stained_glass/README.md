To create a stained glass an image is required. The matlab script reads a configuration file like the following

```
{
  "image": "flower.png",
  "tiles_folder": "tiles/",
  "number_of_tiles": 3,
  "tiles_distortion_factor": 0.05,
  "tiles_rescale_factor": 0.8
}
```

To run the MATLAB script:
```
~/MATLAB/R2018a/bin/matlab -nodisplay -r runme
```

The script creates an OBJ file for each of the "number_of_tiles" tiles in "tiles_folder" folder. These tiles need to be rescaled in order for the skeleton to fit around them later. The rescale factor is specified in the "tiles_rescale_factor" field. If we want the tiles not to be completely smooth a non zero distortion factor must be set in "tiles_distortion_factor" field. An example of an OBJ file of a tile:

![image](https://github.com/andriani-st/mitsuba3-util/assets/77795248/18ed9599-6779-4d66-a44a-b1296741553e)

Also, it creates a colors.txt file including "number_of_tiles" lines each one representing an RGB value for each tile.

Finally, an OBJ file skeleton.obj is created for the skeleton of the stained glass:

![image](https://github.com/andriani-st/mitsuba3-util/assets/77795248/02d68094-5cab-46f6-a391-fd4721b18609)

The paths for the above must be included in the configuration file read by the python script:

```
{
  "output": {
   "type": "image",
   "spp": 2048,
   "width": 512,
   "height": 512
  },
  "camera": {
    "fov": 45
  },
  "lights": {
    "radiance": 10 
  },
  "colors" : "colors.txt",
  "tiles" : "tiles/"
  "objects": [
    {
        "name": "skeleton",
        "filename": "image_surface.obj",
        "material": {
           "type": "metal"
        }
    }
  ]
}
```
And to run the python script:

```
pyhon3 stained_glass.py config.json
```

Finally, the rendered image created is:

![image](https://github.com/andriani-st/mitsuba3-util/assets/77795248/db3e4a5b-3542-47e5-ba3f-a402ee337e92)
