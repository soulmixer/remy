import asyncio
from devices import device
import enums
import json
import logging
import sys
import time

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

class RobotBeforeOven(device.Device):
  """Robot before oven"""

  def __init__(self, name):
    super().__init__(enums.DeviceType.ROBOT_BEFORE_OVEN.value, name)

  async def consumer_handler(self, websocket):
    async for message in websocket:
      print(message)
      data = json.loads(message)
      action = data['action']
      if action == enums.RobotBeforeOvenEvent.PREPARE.value:
        self.pizza['id'] = data['pizza_id']
        self.set_pizza_status(enums.PizzaStatus.IN_PREPARATION.value)
        await self.prepare()
      elif action == enums.RobotBeforeOvenEvent.PUT_IN_OVEN.value:
        await self.put_in_oven()  
        self.set_pizza_status(enums.PizzaStatus.IN_OVEN.value) 
        self.status = enums.RobotBeforeOvenStatus.IDLE.value

  async def prepare(self):
    self.status = enums.RobotBeforeOvenStatus.PREPARING.value
    await self.spread_tomato()
    await self.scatter_cheese()
    self.status = enums.RobotBeforeOvenStatus.WAITING_FOR_OVEN.value
    self.set_pizza_status(enums.PizzaStatus.WAITING_FOR_OVEN.value)

  def set_pizza_status(self, status):
    self.pizza['status'] = status

  async def spread_tomato(self):
    """Spreads tomato sauce on a pizza crust."""

    await self.execute_task('spread_tomato')

  async def scatter_cheese(self):
    """Scatters cheese over tomato sauce."""

    await self.execute_task('scatter_cheese')

  async def put_in_oven(self):
    """Places pizza in one of the ovens."""

    await self.execute_task('place_pizza')
    self.status = enums.RobotBeforeOvenStatus.PIZZA_IN_OVEN.value


class RobotAfterOven(device.Device):
  """Robot after oven"""

  def __init__(self, name):
    super().__init__(enums.DeviceType.ROBOT_AFTER_OVEN.value, name)

  async def consumer_handler(self, websocket):
    async for message in websocket:
      print(message)

  def pick_pizza(self):
    """Picks pizza from one of the ovens."""

    self.execute_task('pick_pizza')
    self.slice_pizza()
    self.pack_pizza()
  
  def slice_pizza(self):
    """Slices pizza into pieces."""

    self.execute_task('slice_pizza')

  def pack_pizza(self):
    """Packs pizza into the box."""

    self.execute_task('pack_pizza')
  