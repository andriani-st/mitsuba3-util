import json
import mitsuba 

class Object:
  def __init__(self, data):
    self.name = data['name']
    self.filename = data['filename']

    material = data['material']

    if material['type'] == 'glass':
      self. material = {'type': 'dielectric', 'int_ior': 'bk7', 'ext_ior': 'air'}
    elif material['type'] == 'roughglass':
      alpha = 0.1
      if 'alpha' in material:
        alpha = material['alpha']
      self. material = {'type': 'roughdielectric', 'distribution': 'beckmann', 'alpha': alpha, 'int_ior': 'bk7', 'ext_ior': 'air'}
    elif material['type'] == 'thinglass':
      self. material = {'type': 'thindielectric', 'int_ior': 'bk7', 'ext_ior': 'air'}
    if material['type'] == 'plastic':
      color = [0.1, 0.27, 0.36]
      if 'color' in material:
        color = material[color]
      self. material = {'type': 'plastic', 'diffuse_reflectance': {'type': 'rgb', 'value': color}}
    elif material['type'] == 'roughplastic':
      color = [0.1, 0.27, 0.36]
      if 'color' in material:
        color = material[color]
      self. material = {'type': 'roughplastic', 'distribution': 'beckmann', 'diffuse_reflectance': {'type': 'rgb', 'value': color}}
    else:
      self.material = material
      
    print(self.material)
    


    

  

    