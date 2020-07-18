import sys
sys.path.append('..')
from client import enums
from devices import device


class Oven(device.Device):
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

  async def cooking_handler(self, orders, 
      queue_outgoing_messages):
    if self.status == enums.OvenStatus.IDLE.value:
      pizzas_waiting = self.filter_by_status(
        orders.orders_in_preparation,
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
        orders.orders_in_preparation,
        [enums.PizzaStatus.IN_OVEN.value])
      for pizza in pizzas_in_oven:
        if self.pizza_id == pizza.id:
          message = self.get_message(action = enums.OvenEvent.COOK.value)
          queue_outgoing_messages.put((self, message))
          break
    elif self.status == enums.OvenStatus.DONE.value:
      pizzas_packing_or_done = self.filter_by_status(
        orders.orders_in_preparation,
        [enums.PizzaStatus.PACKING.value, enums.PizzaStatus.DONE.value])
      for pizza in pizzas_packing_or_done:
        if self.pizza_id == pizza.id:
          message = self.get_message(action = enums.OvenEvent.RESET.value)
          queue_outgoing_messages.put((self, message))
          break