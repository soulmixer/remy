import asyncio
from devices import device
import enums
import json
import time


class Oven(device.Device):
  """Oven device"""

  def __init__(self, name):
    super().__init__(enums.DeviceType.OVEN.value, name)
    self.status = enums.OvenStatus.IDLE.value
    
  async def consumer_handler(self, websocket):
    async for message in websocket:
      data = json.loads(message)
      action = data['action']
      if action == enums.OvenEvent.OPEN.value:
        self.pizza['id'] = data['pizza_id']
        await self.open_front_door()
      elif action == enums.OvenEvent.COOK.value:
        self.pizza['status'] = enums.PizzaStatus.COOKING.value
        await self.close_front_door()
        await self.cook()
        await self.open_back_door()

  async def open_front_door(self):
    """Opens the front door."""
    
    self.status = enums.OvenStatus.OPEN.value
    await self.execute_task('open_front_door')
    await self.send()

  async def close_front_door(self):
    """Closes the front door."""

    await self.execute_task('close_front_door')

  async def open_back_door(self):
    """Opens the back door."""

    await self.execute_task('open_back_door')

  def close_back_door(self):
    """Closes the back door."""

    self.execute_task('close_back_door')

  async def cook(self):
    """Cooks the pizza."""

    await self.execute_task('cook_pizza')

 