import asyncio
import sys
sys.path.append('..')
import json
import logging
import queue
import threading
import time
import websockets

from client import enums
from recipes.pizza import Pizza
from devices.device import Device


logging.basicConfig()

class Kitchen(object):
  """The Kitchen class.

  Attributes:
    queue_pizzas_orders: A queue, the pizzas to prepare.
    pizzas_in_preparation: A list, the pizzas being prepared.
    queue_outgoing_messages: A queue, the messages to send.
    devices: A dict, the list of registered devices. 
    loop: THe event loop.
  """

  def __init__(self):
    num_pizzas_to_prepare = 9

    self.queue_pizzas_orders = queue.Queue()
    self.pizzas_in_preparation = {}
    self.queue_outgoing_messages = queue.Queue()
    self.devices = {
      enums.DeviceType.ROBOT_BEFORE_OVEN.value: {},
      enums.DeviceType.OVEN.value: {},
      enums.DeviceType.ROBOT_AFTER_OVEN.value: {}
    }
    self.loop = None

    for _ in range(num_pizzas_to_prepare):
      self.queue_pizzas_orders.put(Pizza())

    self.open()

  def open(self):
    """Starts the websocket server."""

    start_server = websockets.serve(self.handler, 'localhost', 8765)
    self.loop = asyncio.get_event_loop()
    self.loop.set_debug(True)
    self.loop.slow_callback_duration = 0.1
    self.loop.run_until_complete(start_server)
    self.loop.run_until_complete(self.producer_handler())
    self.loop.run_forever()
    self.loop.close()

  async def handler(self, websocket, path):
    """Handles new websocket connection."""
    
    message = await websocket.recv()
    data = json.loads(message)
    id = data['id']
    type = data['type']
    status = data['status']
    device = Device(id, type, status, websocket)    

    self.devices[type][id] = device

    consumer_task = asyncio.create_task(
      self.consumer_handler(websocket, path))
    cooking_task = asyncio.create_task(
      self.cooking_handler(websocket, path, device))
    done, pending = await asyncio.wait(
      [consumer_task, cooking_task],
      return_when = asyncio.FIRST_COMPLETED,
    )

    for task in pending:
      task.cancel()

  async def consumer_handler(self, websocket, path):
    """Handles websocket incoming messages."""

    async for message in websocket:
      await self.consumer(message)

  async def consumer(self, message):
    """Consumes message."""

    data = json.loads(message)
    pizza_data = data['pizza']
    if pizza_data['id']:
      self.pizzas_in_preparation[pizza_data['id']].status = pizza_data['status']   

    self.devices[data['type']][data['id']].status = data['status']

    await asyncio.sleep(.5)

  async def producer_handler(self):
    """Handles outgoing messages queue."""

    while True:
      for p in self.pizzas_in_preparation.values():
        print(p.status)
      print('-------------')

      while not self.queue_outgoing_messages.empty():
        websocket, message = self.queue_outgoing_messages.get()
        await self.send_message(websocket, message)
      await asyncio.sleep(1)
  
  async def cooking_handler(self, websocket, path, device):
    """Routes device."""

    while True:
      type = device.type
      if type == enums.DeviceType.ROBOT_BEFORE_OVEN.value:
        await self.cooking_handler_robot_before_oven(device)
      elif type == enums.DeviceType.OVEN.value:
        await self.cooking_handler_oven(device)
      elif type == enums.DeviceType.ROBOT_AFTER_OVEN.value:
        await self.cooking_handler_robot_after_oven(device)
      
  def filter_pizzas_in_preparation_by_status(self, status):
    """Returns a sub list filtered by status."""

    return [
      p for p in self.pizzas_in_preparation.values()
      if p.status in status
    ]

  async def cooking_handler_robot_before_oven(self, device):
    if device.status == enums.RobotBeforeOvenStatus.IDLE.value:
      if not self.queue_pizzas_orders.empty():
        pizza = self.queue_pizzas_orders.get()
        pizza.robot_before_oven_id = device.id
        self.pizzas_in_preparation[pizza.id] = pizza
        device.status = enums.RobotBeforeOvenStatus.PREPARING.value
        device.pizza_id = pizza.id
        message = self.get_message(
          pizza_id = pizza.id,
          action = enums.RobotBeforeOvenEvent.PREPARE.value
        )
        self.queue_outgoing_messages.put((device.websocket, message))
    elif device.status == enums.RobotBeforeOvenStatus.WAITING_FOR_OVEN.value:
      pizzas_oven_open = self.filter_pizzas_in_preparation_by_status(
        [enums.PizzaStatus.OVEN_OPEN.value])

      for pizza in pizzas_oven_open:
        if pizza.id == device.pizza_id:
          message = self.get_message(
            action = enums.RobotBeforeOvenEvent.PUT_IN_OVEN.value)
          self.queue_outgoing_messages.put((device.websocket, message))
          break

    await asyncio.sleep(.5)

  async def cooking_handler_oven(self, device):
    if device.status == enums.OvenStatus.IDLE.value:
      pizzas_waiting = self.filter_pizzas_in_preparation_by_status(
        [enums.PizzaStatus.WAITING_FOR_OVEN.value])
      for pizza in pizzas_waiting:
        if not pizza.oven_id:
          pizza.oven_id = device.id
          self.pizzas_in_preparation[pizza.id] = pizza
          device.pizza_id = pizza.id
          message = self.get_message(
            pizza_id = pizza.id,
            action = enums.OvenEvent.OPEN.value
          )
          self.queue_outgoing_messages.put((device.websocket, message))
          break
    elif device.status == enums.OvenStatus.OPEN.value:
      pizzas_in_oven = self.filter_pizzas_in_preparation_by_status(
        [enums.PizzaStatus.IN_OVEN.value])
      for pizza in pizzas_in_oven:
        if device.pizza_id == pizza.id:
          message = self.get_message(action = enums.OvenEvent.COOK.value)
          self.queue_outgoing_messages.put((device.websocket, message))
          break
    elif device.status == enums.OvenStatus.DONE.value:
      pizzas_packing_or_done = self.filter_pizzas_in_preparation_by_status(
        [enums.PizzaStatus.PACKING.value, enums.PizzaStatus.DONE.value])
      for pizza in pizzas_packing_or_done:
        if device.pizza_id == pizza.id:
          message = self.get_message(action = enums.OvenEvent.RESET.value)
          self.queue_outgoing_messages.put((device.websocket, message))
          break

    await asyncio.sleep(.5)

  async def cooking_handler_robot_after_oven(self, device):
    if device.status == enums.RobotAfterOvenStatus.IDLE.value:
      pizzas_ready_to_pack = self.filter_pizzas_in_preparation_by_status(
        [enums.PizzaStatus.READY_TO_PACK.value])
      for pizza in pizzas_ready_to_pack:
        if not pizza.robot_after_oven_id:
          pizza.robot_after_oven_id = device.id
          self.pizzas_in_preparation[pizza.id] = pizza
          device.pizza_id = pizza.id
          message = self.get_message(
            pizza_id = pizza.id,
            action = enums.RobotAfterOvenEvent.PACK.value
          )
          self.queue_outgoing_messages.put((device.websocket, message))
          break

    await asyncio.sleep(.5)

  def get_message(self, **message):
    """Gets message."""

    return message

  async def send_message(self, websocket, message):
    """Sends message"""

    await websocket.send(json.dumps(message))