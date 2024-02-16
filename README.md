# mitsuba3-util

This util integrates mitsuba3 and provides a number of options to create rendered images or animations of objects. Also, some more specilised applications were created as described in the README files in stained_glass, filigree and cylinder_orderings folders. 

To run the util
```
python3 util.py /path/to/json/file/config.json
```

By modifying the config.json file accordingly the following outputs are available:
- Rendered png images of specified size and quality
- Rotation videos of specified number of views (e.g. full rotations with 360 views)
- Animation videos by rendering OBJ frames provided
- Rotation videos of animations of specified number of views
