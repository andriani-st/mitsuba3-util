import json
import mitsuba 

class Object:
  def __init__(self, data):
    self.name = data['name']
    self.filename = data['filename']
    self.type = data['type']

    material = data['material']

    if material['type'] == 'glass':
      if 'color' in material:
        color = material['color']
        self.material = {'type': 'dielectric', 'int_ior': 'bk7', 'ext_ior': 'air', 'specular_transmittance': {'type': 'rgb', 'value': color}}
      else:
        self.material = {'type': 'dielectric', 'int_ior': 'bk7', 'ext_ior': 'air'}
    elif material['type'] == 'roughglass':
      alpha = 0.1
      if 'alpha' in material:
        alpha = material['alpha']
      self.material = {'type': 'roughdielectric', 'distribution': 'beckmann', 'alpha': alpha, 'int_ior': 'bk7', 'ext_ior': 'air'}
    elif material['type'] == 'thinglass':
      self.material = {'type': 'thindielectric', 'int_ior': 'bk7', 'ext_ior': 'air'}
    elif material['type'] == 'plastic':
      color = [0.1, 0.27, 0.36]
      if 'color' in material:
        color = material['color']
      self. material = {'type': 'plastic', 'diffuse_reflectance': {'type': 'rgb', 'value': color}}
    elif material['type'] == 'roughplastic':
      alpha = 0.1
      if 'alpha' in material:
        alpha = material['alpha']
      color = [0.1, 0.27, 0.36]
      if 'color' in material:
        color = material['color']
      self. material = {'type': 'roughplastic', 'distribution': 'beckmann', 'alpha': alpha, 'diffuse_reflectance': {'type': 'rgb', 'value': color}}
    elif material['type'] == 'metal':
      self. material = {'type': 'conductor', 'material': 'Au'}
    elif material['type'] == 'roughmetal':
      alpha = 0.1
      if 'alpha' in material:
        alpha = material['alpha']
      self. material = {'type': 'roughconductor', 'material': 'Au', 'distribution': 'ggx', 'alpha_u': alpha, 'alpha_v': alpha}
    elif material['type'] == "diffuse":
      self. material = {'type': 'diffuse'}
    else:
      self.material = material
      
    #print(self.material)
    


    

  

    