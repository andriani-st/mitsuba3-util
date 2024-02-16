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

The script creates an OBJ file for each of the "number_of_tiles" tiles in "tiles_folder" folder. These tiles need to be rescaled in order for the skeleton to fit around them later. The rescale factor is specified in the "tiles_rescale_factor" field. If we want the tiles not to be completely smooth a non zero distortion factor must be set in "tiles_distortion_factor" field. An example of an OBJ file of a tile:

