import mitsuba
import numpy as np

mitsuba.set_variant("cuda_ad_rgb")

from mitsuba import ScalarTransform4f as T

class Camera:
    def __init__(self, fov, distance, object_center, up_axis = np.array([0,1,0]), width = 512, height = 512, spp = 224, rotation_axis = [0,0,0]):
        self.fov = fov
        self.up_axis = up_axis
        
        self.object_center = np.array(object_center)
        self.width = width
        self.height = height
        self.samples_per_pixel = spp

        if(rotation_axis== [0,0,0]):
            self.rotation_axis = up_axis
        else:
            self.rotation_axis = rotation_axis

        if(self.rotation_axis == self.up_axis):
            if(up_axis == [0,1,0]):
                self.origin = np.array([object_center[0],object_center[1],object_center[2]+distance])
                self.side_axis = [1,0,0]
                self.depth_axis = [0,0,1]
            elif(up_axis == [1,0,0]):
                self.origin = np.array([object_center[0],object_center[1],object_center[2]+distance])
                self.side_axis = [0,1,0]
                self.depth_axis = [0,0,1]
            elif(up_axis == [0,0,1]):
                self.origin = np.array([object_center[0],object_center[1]+distance,object_center[2]])
                self.side_axis = [1,0,0]
                self.depth_axis = [0,1,0]
        else:
            free_axis = np.array(self.up_axis) + np.array(self.rotation_axis)
            self.depth_axis = [1-free_axis[0],1-free_axis[1],1-free_axis[2]]

            dummy_axis = np.array(self.depth_axis) + np.array(self.up_axis)
            self.side_axis = [1-dummy_axis[0],1-dummy_axis[1],1-dummy_axis[2]]

            self.origin = np.array([object_center[0] + distance*(1-free_axis[0]),object_center[1] + distance*(1-free_axis[1]),object_center[2] + distance*(1-free_axis[2])])

    def rotate_camera_origin(self, angle):
        theta = np.radians(angle)

        translated_camera_origin = self.origin - self.object_center

        R = np.empty([3, 3])
        if(self.rotation_axis == [0,0,1]):
            R = np.array([[np.cos(theta), -np.sin(theta), 0],
                           [np.sin(theta), np.cos(theta), 0],
                           [0, 0, 1]])
        elif(self.rotation_axis == [0,1,0]):
            R = np.array([[np.cos(theta), 0, np.sin(theta)],
                           [0, 1, 0],
                           [-np.sin(theta), 0, np.cos(theta)]])
        else:
            R = np.array([[1, 0, 0],
                          [0, np.cos(theta), -np.sin(theta)],
                          [0, np.sin(theta), np.cos(theta)]])
            
        rotated_camera_origin = R @ translated_camera_origin

        new_camera_origin = rotated_camera_origin + self.object_center

        return new_camera_origin
    
    def load_sensor(self, angle=0):
        return mitsuba.load_dict({
            'type': 'perspective',
            'fov': self.fov,
            'to_world': T.look_at(origin=self.rotate_camera_origin(angle), target=self.object_center, up=self.up_axis),
            'principal_point_offset_x': 0,  #normalized principal point, [0,0] -> center of image
            'principal_point_offset_y': 0,
            'sampler': {
                'type': 'multijitter',
                'sample_count': self.samples_per_pixel
            },
            'film': {
                'type': 'hdrfilm',
                'width': self.width,
                'height': self.height,
                'rfilter': {
                    'type': 'tent',
                },
                'pixel_format': 'rgb',
            },
        })
