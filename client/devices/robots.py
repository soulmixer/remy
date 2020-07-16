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
        """
        await asyncio.sleep(1)
        self.pizza = {
          'id': None, 
          'status': None
        }
        """

  async def prepare(self):
    self.status = enums.RobotBeforeOvenStatus.PREPARING.value
    await self.spread_tomato()
    await self.scatter_cheese()
    self.status = enums.RobotBeforeOvenStatus.WAITING_FOR_OVEN.value
    self.set_pizza_status(enums.PizzaStatus.WAITING_FOR_OVEN.value)

  async def spread_tomato(self):
    """Spreads tomato sauce on a pizza crust."""

    await self.execute_task('spread_tomato')

  async def scatter_cheese(self):
    """Scatters cheese over tomato sauce."""

    await self.execute_task('scatter_cheese')

  async def put_in_oven(self):
    """Places pizza in one of the ovens."""

    await self.execute_task('put_in_oven')
    self.status = enums.RobotBeforeOvenStatus.PIZZA_IN_OVEN.value


class RobotAfterOven(device.Device):
  """Robot after oven"""

  def __init__(self, name):
    super().__init__(enums.DeviceType.ROBOT_AFTER_OVEN.value, name)

  async def consumer_handler(self, websocket):
    async for message in websocket:
      data = json.loads(message)
      action = data['action']
      if action == enums.RobotAfterOvenEvent.PACK.value:
        self.pizza['id'] = data['pizza_id']
        self.status = enums.RobotAfterOvenStatus.PACKING.value
        self.set_pizza_status(enums.PizzaStatus.PACKING.value)
        await self.prepare()
        self.set_pizza_status(enums.PizzaStatus.DONE.value)
        self.status = enums.RobotAfterOvenStatus.IDLE.value
        """
        await asyncio.sleep(1)
        self.pizza = {
          'id': None, 
          'status': None
        }
        """

  async def prepare(self):
    """Prepares pizza."""

    await self.pick()
    await self.slice()
    await self.pack()

  async def pick(self):
    """Picks pizza from one of the ovens."""

    await self.execute_task('pick')
  
  async def slice(self):
    """Slices pizza into pieces."""

    await self.execute_task('slice_pizza')

  async def pack(self):
    """Packs pizza into the box."""

    await self.execute_task('pack_pizza')