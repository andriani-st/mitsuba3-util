# mitsuba3-util

The purpose of mitsuba3-util is to simplify the use of mitsuba3 for rendering images and extend its output options. 

The util integrates mitsuba3 and provides a number of options to create rendered images or animations of objects. Also, some more specilised applications were created as described in the README files in stained_glass, filigree and cylinder_orderings folders. 


## Prerequisites
- Python 3.8.0

- mitsuba3 (https://mitsuba.readthedocs.io/en/latest/)
```
pip install mitsuba
```

- OpenCV (https://pypi.org/project/opencv-python/)
```
pip install opencv-python
```
- MATLAB

## Running the util

To run the util

```
python3 util.py /path/to/json/file/config.json
```

> Renders image/video using config.json

or

```
python3 util.py /path/to/folder/containing/multiple/json/files/
```

For more information see the user manual: 
