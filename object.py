from config import ObjectConfig

class Object:
  def __init__(self, data : ObjectConfig):
    self.name = data.name
    self.filename = data.filename
    self.type = data.type
    self.x_rotation_degrees = data.object_x_rotation_degrees
    self.y_rotation_degrees = data.object_y_rotation_degrees
    self.z_rotation_degrees = data.object_z_rotation_degrees

    self.material = Material(data.material_type, data.material_color, data.material_alpha, data.metal_type, data.material_dict)
 
  def get_transform(self):
    from mitsuba import ScalarTransform4f as T

    rotation_x = T.rotate(axis=[1, 0, 0], angle=self.x_rotation_degrees)
    rotation_y = T.rotate(axis=[0, 1, 0], angle=self.y_rotation_degrees)
    rotation_z = T.rotate(axis=[0, 0, 1], angle=self.z_rotation_degrees)

    return rotation_z @ rotation_y @ rotation_x

  # geometry-only dict used for bounding box calculation in scene.py
  def to_geometry_dict(self):
    return {
      'type': self.type,
      'filename': self.filename,
      'to_world': self.get_transform()
    }

  def to_mitsuba_dict(self):
    return {
      'type': self.type,
      'filename': self.filename,
      'bsdf': self.material.to_mitsuba_dict(),
      'to_world': self.get_transform()
    }

class Material:
  def __init__(self, material_type, material_color, material_alpha, metal_type, material_dict):
    self.type = material_type
    self.color = material_color
    self.alpha = material_alpha
    self.metal_type = metal_type
    self.material_dict = material_dict

  def to_mitsuba_dict(self):
    if self.type == 'glass':
      if self.color == "auto":
        return {'type': 'dielectric', 'int_ior': 'bk7', 'ext_ior': 'air'}
      else:
        return {'type': 'dielectric', 'int_ior': 'bk7', 'ext_ior': 'air', 'specular_transmittance': {'type': 'rgb', 'value': self.color}}

    elif self.type == 'roughglass':
      if self.color == "auto":
        return {'type': 'roughdielectric', 'distribution': 'beckmann', 'alpha': self.alpha, 'int_ior': 'bk7', 'ext_ior': 'air'}
      else:
        return {'type': 'roughdielectric', 'distribution': 'beckmann', 'alpha': self.alpha, 'int_ior': 'bk7', 'ext_ior': 'air', 'specular_transmittance': {'type': 'rgb', 'value': self.color}}
    elif self.type == 'thinglass':
      if self.color == "auto":
        return {'type': 'thindielectric', 'int_ior': 'bk7', 'ext_ior': 'air'}
      else:
        return {'type': 'thindielectric', 'int_ior': 'bk7', 'ext_ior': 'air', 'specular_transmittance': {'type': 'rgb', 'value': self.color}}
    
    elif self.type == 'plastic':
      return {'type': 'plastic', 'diffuse_reflectance': {'type': 'rgb', 'value': self.color}}
    
    elif self.type == 'roughplastic':
      return {'type': 'roughplastic', 'distribution': 'beckmann', 'alpha': self.alpha, 'diffuse_reflectance': {'type': 'rgb', 'value': self.color}}
    
    elif self.type == 'metal':
      return {'type': 'conductor', 'material': self.metal_type}
    
    elif self.type == 'roughmetal':
      return {'type': 'roughconductor', 'material': self.metal_type, 'distribution': 'ggx', 'alpha_u': self.alpha, 'alpha_v': self.alpha}
    
    else:
      return self.material_dict
    