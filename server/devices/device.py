import sys
sys.path.append('..')
from client import enums

class Device(object):
  """"Device."""

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
    

class RobotBeforeOven(Device):
  """Robot Before Oven."""

  def __init__(self, id, type, status, websocket):
    super().__init__(id, type, status, websocket)

  @property
  def status(self):
    return self._status

  @status.setter
  def status(self, status):
    if ((self._status == enums.RobotBeforeOvenStatus.IDLE.value and
         status == enums.RobotBeforeOvenStatus.PREPARING.value) or
        (self._status == enums.RobotBeforeOvenStatus.PREPARING.value and
         status == enums.RobotBeforeOvenStatus.WAITING_FOR_OVEN.value) or
        (self._status == enums.RobotBeforeOvenStatus.WAITING_FOR_OVEN.value and
         status == enums.RobotBeforeOvenStatus.PIZZA_IN_OVEN.value) or
        (self._status == enums.RobotBeforeOvenStatus.PIZZA_IN_OVEN.value and
         status == enums.RobotBeforeOvenStatus.IDLE.value)):
      self._status = status


class Oven(Device):
  """Oven."""

  def __init__(self, id, type, status, websocket):
    super().__init__(id, type, status, websocket)
 
  @property
  def status(self):
    return self._status

  @status.setter
  def status(self, status):
    if ((self._status == enums.OvenStatus.IDLE.value and
         status == enums.OvenStatus.OPEN.value) or
        (self._status == enums.OvenStatus.OPEN.value and
         status == enums.OvenStatus.COOKING.value) or
        (self._status == enums.OvenStatus.COOKING.value and
         status == enums.OvenStatus.DONE.value) or
        (self._status == enums.OvenStatus.DONE.value and
         status == enums.OvenStatus.IDLE.value)):
      self._status = status

class RobotAfterOven(Device):
  """Robot Before Oven."""

  def __init__(self, id, type, status, websocket):
    super().__init__(id, type, status, websocket)

  @property
  def status(self):
    return self._status

  @status.setter
  def status(self, status):
    if ((self._status == enums.RobotAfterOvenStatus.IDLE.value and
         status == enums.RobotAfterOvenStatus.PACKING.value) or
        (self._status == enums.RobotAfterOvenStatus.PACKING.value and
         status == enums.RobotAfterOvenStatus.IDLE.value)):
      self._status = status
    