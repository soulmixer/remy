class Device(object):
  """"Device"""

  def __init__(self, id, type, status, websocket, pizza_id = None):
    self._id = id
    self._type = type
    self._status = status
    self.websocket = websocket
    self._pizza_id = pizza_id

  @property
  def id(self):
    return self._id

  @property
  def type(self):
    return self._type

  @property
  def status(self):
    return self._status
  
  @status.setter
  def status(self, status):
    self._status = status

  @property
  def pizza_id(self):
    return self._pizza_id

  @pizza_id.setter
  def pizza_id(self, id):
    self._pizza_id = id
    