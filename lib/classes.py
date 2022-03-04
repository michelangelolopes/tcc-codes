class Academic:
  def __init__(self):
    self.has_covid = False
    self.can_transmit = False
    # self.has_symptoms = False # talvez remover, já que não é utilizado
    self.infected_days = 0
    self.infection_probability = 0
    self.breathing_rate = 0

class Student(Academic):
  def __init__(self, id, course):
    Academic.__init__(self)
    self.id = id
    self.course = course

class Professor(Academic):
  def __init__(self, name):
    Academic.__init__(self)
    self.name = name
    
class Classroom:
  def __init__(self, height, width, length):
    self.volume = length * width * height
    # self.height = height
    # self.width = width
    # self.length = length
    # self.has_outside_opening = has_outside_opening
