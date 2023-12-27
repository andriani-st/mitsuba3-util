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
      self. material = {'type': 'roughdielectric', 'distribution': 'beckmann', 'alpha': 0.1, 'int_ior': 'bk7', 'ext_ior': 'air'}
    elif material['type'] == 'thinglass':
      self. material = {'type': 'thindielectric', 'int_ior': 'bk7', 'ext_ior': 'air'}
    else:
      self.material = material
      
    print(self.material)
    


    

  

    