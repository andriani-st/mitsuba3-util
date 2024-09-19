**This repository contains software that serves as part of the requirements for my Master's thesis at the University of Crete. The software is also part of the “Craeft” Research and Innovation Action, funded by the European Commission under the Horizon Europe programme (Grant Agreement No. 101094349).**

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

-Various Python libraries
```
pip install -r requirements.txt
```

- MATLAB

## Running the util

To run the util

```
python3 util.py /path/to/json/file/config.json
```

> Renders image/video using config.json


## User manual

The user manual can be found here: https://github.com/andriani-st/mitsuba3-util/blob/main/user_manual_v_03.pdf



