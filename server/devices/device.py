import json
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
    
  def get_message(self, **message):
    """Gets message."""

    return message

  def filter_by_status(self, pizzas, status):
    """Returns a sub list filtered by status."""

    return [
      p for p in pizzas.values()
      if p.status in status
    ]

  async def send_message(self, message):
    """Sends message"""

    await self.websocket.send(json.dumps(message))


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

  async def cooking_handler(self, queue_pizzas_orders, pizzas_in_preparation, 
      queue_outgoing_messages):
    if self.status == enums.RobotBeforeOvenStatus.IDLE.value:
      if not queue_pizzas_orders.empty() and not self.pizza_id:
        pizza = queue_pizzas_orders.get()
        pizza.robot_before_oven_id = self.id
        pizzas_in_preparation[pizza.id] = pizza
        self.status = enums.RobotBeforeOvenStatus.PREPARING.value
        self.pizza_id = pizza.id
        message = self.get_message(
          pizza_id = pizza.id,
          action = enums.RobotBeforeOvenEvent.PREPARE.value
        )
        queue_outgoing_messages.put((self, message))
    elif self.status == enums.RobotBeforeOvenStatus.WAITING_FOR_OVEN.value:
      pizzas_oven_open = self.filter_by_status(
        pizzas_in_preparation, [enums.PizzaStatus.OVEN_OPEN.value])
      for pizza in pizzas_oven_open:
        if pizza.id == self.pizza_id:
          message = self.get_message(
            action = enums.RobotBeforeOvenEvent.PUT_IN_OVEN.value)
          queue_outgoing_messages.put((self, message))
          break

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

  async def cooking_handler(self, pizzas_in_preparation, 
      queue_outgoing_messages):
    if self.status == enums.OvenStatus.IDLE.value:
      pizzas_waiting = self.filter_by_status(
        pizzas_in_preparation,
        [enums.PizzaStatus.WAITING_FOR_OVEN.value])
      for pizza in pizzas_waiting:
        if not pizza.oven_id:
          pizza.oven_id = self.id
          self.pizza_id = pizza.id
          message = self.get_message(
            pizza_id = pizza.id,
            action = enums.OvenEvent.OPEN.value
          )
          queue_outgoing_messages.put((self, message))
          break
    elif self.status == enums.OvenStatus.OPEN.value:
      pizzas_in_oven = self.filter_by_status(
        pizzas_in_preparation,
        [enums.PizzaStatus.IN_OVEN.value])
      for pizza in pizzas_in_oven:
        if self.pizza_id == pizza.id:
          message = self.get_message(action = enums.OvenEvent.COOK.value)
          queue_outgoing_messages.put((self, message))
          break
    elif self.status == enums.OvenStatus.DONE.value:
      pizzas_packing_or_done = self.filter_by_status(
        pizzas_in_preparation,
        [enums.PizzaStatus.PACKING.value, enums.PizzaStatus.DONE.value])
      for pizza in pizzas_packing_or_done:
        if self.pizza_id == pizza.id:
          message = self.get_message(action = enums.OvenEvent.RESET.value)
          queue_outgoing_messages.put((self, message))
          break


class RobotAfterOven(Device):
  """Robot After Oven."""

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

  async def cooking_handler(self, pizzas_in_preparation, 
      queue_outgoing_messages):
    if self.status == enums.RobotAfterOvenStatus.IDLE.value:
      pizzas_ready_to_pack = self.filter_by_status(
        pizzas_in_preparation, [enums.PizzaStatus.READY_TO_PACK.value])
      for pizza in pizzas_ready_to_pack:
        if not pizza.robot_after_oven_id:
          pizza.robot_after_oven_id = self.id
          pizzas_in_preparation[pizza.id] = pizza
          self.pizza_id = pizza.id
          message = self.get_message(
            pizza_id = pizza.id,
            action = enums.RobotAfterOvenEvent.PACK.value
          )
          queue_outgoing_messages.put((self, message))
          break
    