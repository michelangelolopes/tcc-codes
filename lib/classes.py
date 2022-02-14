class Academic:
  def __init__(self):
    self.hasCovid = False
    self.canTransmit = False
    self.hasSymptoms = False # talvez remover, já que não é utilizado
    self.countInfectedTime = 0
    self.infectionProbability = 0

class Student(Academic):
  def __init__(self, id, course):
    Academic.__init__(self)
    self.id = id
    self.course = course

class Professor(Academic):
  def __init__(self, name):
    Academic.__init__(self)
    self.name = name
    