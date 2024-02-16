To create a metal filigree a black and white image representing a pattern is required. First, run the .m script:
```
matlab -nodisplay -r runme_with_colors_ref
```
This script generates an OBJ file named image_surface.obj, which embodies the 3D geometry of a rectangular surface matching the dimensions of the provided image. The pattern depicted in the image is "carved" onto this surface.

![image](https://github.com/andriani-st/mitsuba3-util/assets/77795248/98933c04-e570-4e71-9951-de2c84e1d1a1)



The path to the OBJ file must be entered in the configuration file that will be read by the python script. 
A simple example of a configuration file for the creation of a metal filigree is the following:
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
  "objects": [
    {
        "name": "surface",
        "filename": "image_surface.obj",
        "material": {
           "type": "metal"
        }
    }
  ]
}
```
The python script must then be executed with:
```
python3 filigree_room.py config.json 
```
And the rendered image that is created:

![image](https://github.com/andriani-st/mitsuba3-util/assets/77795248/a6c1571d-637d-4a0d-9cba-e9a4b515c9e2)

