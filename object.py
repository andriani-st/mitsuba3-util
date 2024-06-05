from config import ObjectConfig

class Object:
  def __init__(self, data : ObjectConfig):
    self.name = data.name
    self.filename = data.filename
    self.type = data.type

    if data.material_type == 'glass':
      if data.material_color == "auto":
        self.material = {'type': 'dielectric', 'int_ior': 'bk7', 'ext_ior': 'air'}
      else:
        self.material = {'type': 'dielectric', 'int_ior': 'bk7', 'ext_ior': 'air', 'specular_transmittance': {'type': 'rgb', 'value': data.material_color}}
  
    elif data.material_type == 'roughglass':
      self.material = {'type': 'roughdielectric', 'distribution': 'beckmann', 'alpha': data.material_alpha, 'int_ior': 'bk7', 'ext_ior': 'air'}
    
    elif data.material_type == 'thinglass':
      self.material = {'type': 'thindielectric', 'int_ior': 'bk7', 'ext_ior': 'air'}
    
    elif data.material_type == 'plastic':
      self.material = {'type': 'plastic', 'diffuse_reflectance': {'type': 'rgb', 'value': data.material_color}}
    
    elif data.material_type == 'roughplastic':
      self.material = {'type': 'roughplastic', 'distribution': 'beckmann', 'alpha': data.material_alpha, 'diffuse_reflectance': {'type': 'rgb', 'value': data.material_color}}
    
    elif data.material_type == 'metal':
      self.material = {'type': 'conductor', 'material': data.metal_type}
    
    elif data.material_type == 'roughmetal':
      self.material = {'type': 'roughconductor', 'material': data.metal_type, 'distribution': 'ggx', 'alpha_u': data.material_alpha, 'alpha_v': data.material_alpha}
    
    elif data.material_type == "diffuse":
      self.material = {'type': 'diffuse'}
    
    else:
      self.material = data.material
 
    


    

  

    