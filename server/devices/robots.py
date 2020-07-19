import sys
sys.path.append('..')
from client import enums
from devices.device import Device


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

  async def cooking_handler(self, orders, queue_outgoing_messages):
    if self.status == enums.RobotBeforeOvenStatus.IDLE.value:
      if not orders.queue_orders.empty() and not self.pizza_id:
        pizza = orders.queue_orders.get()
        pizza.robot_before_oven_id = self.id
        orders.orders_in_preparation[pizza.id] = pizza
        self.status = enums.RobotBeforeOvenStatus.PREPARING.value
        self.pizza_id = pizza.id
        message = self.get_message(
          pizza_id = pizza.id,
          action = enums.RobotBeforeOvenEvent.PREPARE.value
        )
        queue_outgoing_messages.put((self, message))
    elif self.status == enums.RobotBeforeOvenStatus.WAITING_FOR_OVEN.value:
      pizzas_oven_open = self.filter_by_status(
        orders.orders_in_preparation, [enums.PizzaStatus.OVEN_OPEN.value])
      for pizza in pizzas_oven_open:
        if pizza.id == self.pizza_id:
          message = self.get_message(
            action = enums.RobotBeforeOvenEvent.PUT_IN_OVEN.value)
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

  async def cooking_handler(self, orders, queue_outgoing_messages):
    if self.status == enums.RobotAfterOvenStatus.IDLE.value:
      pizzas_ready_to_pack = self.filter_by_status(
        orders.orders_in_preparation, [enums.PizzaStatus.READY_TO_PACK.value])
      for pizza in pizzas_ready_to_pack:
        if not pizza.robot_after_oven_id:
          pizza.robot_after_oven_id = self.id
          orders.orders_in_preparation[pizza.id] = pizza
          self.pizza_id = pizza.id
          message = self.get_message(
            pizza_id = pizza.id,
            action = enums.RobotAfterOvenEvent.PACK.value
          )
          queue_outgoing_messages.put((self, message))
          break
    