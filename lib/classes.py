class Student:
  def __init__(self, id, course, hasCovid = False, canTransmit = False, hasSymptoms = False, countInfectedTime = 0, infectionProbability = 0.0):
    self.id = id
    self.course = course
    self.hasCovid = hasCovid
    self.canTransmit = canTransmit
    self.hasSymptoms = hasSymptoms
    self.countInfectedTime = countInfectedTime
    self.infectionProbability = infectionProbability
