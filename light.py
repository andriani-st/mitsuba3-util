from config import LightConfig

class Light:
    def __init__(self, data : LightConfig, to_world=None):
        self.emitter_type = data.emitter_type
        self.to_world = to_world

        if self.emitter_type == "envmap":
            self.envmap_filename = data.envmap_filename
            self.envmap_rotation_axis = data.envmap_rotation_axis
            self.envmap_rotation_degrees = data.envmap_rotation_degrees
            self.envmap_scale_factor = data.envmap_scale_factor

        if self.emitter_type == "area":
            self.emitter_shape = data.emitter_shape
            self.emitter_radiance = data.emitter_radiance
            self.emitter_size = data.emitter_size
            self.emitter_distance_from_object = data.emitter_distance_from_object
            self.emitter_position = data.emitter_position
            self.emitter_rotation_axis = data.emitter_rotation_axis
            self.emitter_rotation_degrees = data.emitter_rotation_degrees

    def to_mitsuba_dict(self):
        if self.emitter_type == "envmap":
                return self._envmap_to_mitsuba_dict()
        elif self.emitter_type == "area":
            return self._area_to_mitsuba_dict()

    def _envmap_to_mitsuba_dict(self):
        from mitsuba import ScalarTransform4f as T

        return {
            "type": "envmap",
            "filename": self.envmap_filename,
            "to_world": T.rotate(self.envmap_rotation_axis, self.envmap_rotation_degrees),
            "scale": self.envmap_scale_factor,
        }

    def _area_to_mitsuba_dict(self):
        return {
            'type': self.emitter_shape, 
            'to_world': self.to_world, 
            'bsdf': {
            'type': 'diffuse',
                'reflectance': {
                    'type': 'rgb',
                    'value': [1,1,1]
                }
            },
            'emitter': {
                'type': self.emitter_type, 
                'radiance': {
                    'type': 'rgb', 
                    'value': self.emitter_radiance
                }
            }
        }

    