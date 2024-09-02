from config import ObjectConfig

class Object:
  def __init__(self, data : ObjectConfig):
    self.name = data.name
    self.filename = data.filename
    self.type = data.type
    self.rotation_axis = data.rotation_axis
    self.rotation_degrees = data.rotation_degrees
    self.x_rotation_degrees = data.x_rotation_degrees
    self.y_rotation_degrees = data.y_rotation_degrees
    self.z_rotation_degrees = data.z_rotation_degrees

    if data.material_type == 'glass':
      if data.material_color == "auto":
        self.material = {'type': 'dielectric', 'int_ior': 'bk7', 'ext_ior': 'air'}
      else:
        self.material = {'type': 'dielectric', 'int_ior': 'bk7', 'ext_ior': 'air', 'specular_transmittance': {'type': 'rgb', 'value': data.material_color}}
  
    elif data.material_type == 'roughglass':
      if data.material_color == "auto":
        self.material = {'type': 'roughdielectric', 'distribution': 'beckmann', 'alpha': data.material_alpha, 'int_ior': 'bk7', 'ext_ior': 'air'}
      else:
        self.material = {'type': 'roughdielectric', 'distribution': 'beckmann', 'alpha': data.material_alpha, 'int_ior': 'bk7', 'ext_ior': 'air', 'specular_transmittance': {'type': 'rgb', 'value': data.material_color}}
    elif data.material_type == 'thinglass':
      if data.material_color == "auto":
        self.material = {'type': 'thindielectric', 'int_ior': 'bk7', 'ext_ior': 'air'}
      else:
        self.material = {'type': 'thindielectric', 'int_ior': 'bk7', 'ext_ior': 'air', 'specular_transmittance': {'type': 'rgb', 'value': data.material_color}}
    
    elif data.material_type == 'plastic':
      self.material = {'type': 'plastic', 'diffuse_reflectance': {'type': 'rgb', 'value': data.material_color}}
    
    elif data.material_type == 'roughplastic':
      self.material = {'type': 'roughplastic', 'distribution': 'beckmann', 'alpha': data.material_alpha, 'diffuse_reflectance': {'type': 'rgb', 'value': data.material_color}}
    
    elif data.material_type == 'metal':
      self.material = {'type': 'conductor', 'material': data.metal_type}
    
    elif data.material_type == 'roughmetal':
      self.material = {'type': 'roughconductor', 'material': data.metal_type, 'distribution': 'ggx', 'alpha_u': data.material_alpha, 'alpha_v': data.material_alpha}
    
    else:
      self.material = data.material
 
    


    

  

    