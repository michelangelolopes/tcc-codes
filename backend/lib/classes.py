class Academic:
  def __init__(self):
    self.academic_id = ""
    # self.has_covid = False
    # self.can_transmit = False
    # self.has_symptoms = False # talvez remover, já que não é utilizado
    # self.infected_days = 0
    self.infection_probability = []
    self.comb_prob = []
    # self.breathing_rate = 0

class Student(Academic):
  def __init__(self, registration_number = "", course = ""):
    Academic.__init__(self)
    self.id = ""
    self.registration_number = registration_number
    self.course = course

class Professor(Academic):
  def __init__(self, name = ""):
    Academic.__init__(self)
    self.id = ""
    self.name = name
    
class Classroom:
  def __init__(self, id, type):
    self.id = id
    self.type = type
    # self.has_outside_opening = has_outside_opening

class Classroom_Type:
  def __init__(self, type, height, width, length):
    self.type = type
    self.height = height
    self.width = width
    self.length = length
    self.volume = length * width * height
