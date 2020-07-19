import uuid
import sys
sys.path.append('..')
from client import enums


class Pizza(object):
  """Pizza"""

  def __init__(self):
    self._id = str(uuid.uuid4())
    self._status = enums.PizzaStatus.NOT_STARTED.value
    self._robot_before_oven_id = None
    self._oven_id = None
    self._robot_after_oven_id = None

  @property
  def id(self):
    return self._id

  @property
  def status(self):
    return self._status
  
  @status.setter
  def status(self, status):
    if ((self._status == enums.PizzaStatus.NOT_STARTED.value 
         and status == enums.PizzaStatus.IN_PREPARATION.value) or
        (self._status == enums.PizzaStatus.IN_PREPARATION.value 
         and status == enums.PizzaStatus.WAITING_FOR_OVEN.value) or
        (self._status == enums.PizzaStatus.WAITING_FOR_OVEN.value 
         and status == enums.PizzaStatus.OVEN_OPEN.value) or
        (self._status == enums.PizzaStatus.OVEN_OPEN.value 
         and status == enums.PizzaStatus.IN_OVEN.value) or
        (self._status == enums.PizzaStatus.IN_OVEN.value 
         and status == enums.PizzaStatus.COOKING.value) or
        (self._status == enums.PizzaStatus.COOKING.value 
         and status == enums.PizzaStatus.READY_TO_PACK.value) or
        (self._status == enums.PizzaStatus.READY_TO_PACK.value 
         and status == enums.PizzaStatus.PACKING.value) or
        (self._status == enums.PizzaStatus.PACKING.value 
         and status == enums.PizzaStatus.DONE.value)):

      self._status = status
    
  @property
  def robot_before_oven_id(self):
    return self._robot_before_oven_id

  @robot_before_oven_id.setter
  def robot_before_oven_id(self, id):
    self._robot_before_oven_id = id
  
  @property
  def oven_id(self):
    return self._oven_id

  @oven_id.setter
  def oven_id(self, id):
    self._oven_id = id

  @property
  def robot_after_oven_id(self):
    return self._robot_after_oven_id
  
  @robot_after_oven_id.setter
  def robot_after_oven_id(self, id):
    self._robot_after_oven_id = id
