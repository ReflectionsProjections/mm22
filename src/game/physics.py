class Point(object):
  def __init__(self, x, y):
    self.x = x
    self.y = y


class LineSeg(object):
  def __init__(self, point1, point2):
    self.endpoint_1 = point1
    self.endpoint_2 = point2

  # def lineseg_is_intersecting(lineseg_1, lineseg_2):
