class Academic:
  def __init__(self, hasCovid = False, canTransmit = False, hasSymptoms = False, countInfectedTime = 0, infectionProbability = 0.0):
    self.hasCovid = hasCovid
    self.canTransmit = canTransmit
    self.hasSymptoms = hasSymptoms
    self.countInfectedTime = countInfectedTime
    self.infectionProbability = infectionProbability

class Student(Academic):
  def __init__(self, id, course):
    self.id = id
    self.course = course

class Professor(Academic):
  def __init__(self, name):
    self.name = name
    self.subjects = []
    