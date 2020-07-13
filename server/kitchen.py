import asyncio
import sys
sys.path.append('..')
import json
import logging
import queue
import time
import websockets

from client import enums
from recipes.pizza import Pizza
from devices.device import Device


logging.basicConfig()

class Kitchen(object):
  """The Kitchen class.

  Attributes:
    devices: A dict, the list of registered devices. 
    queue_robots_before_ovens: A queue, the pizzas to prepare.
    pizzas_in_preparation: A list, the pizzas being prepared.
  """

  def __init__(self):
    num_pizzas_to_prepare = 4

    self.queue_robots_before_ovens = queue.Queue()
    self.queue_messages = queue.Queue()
    self.queue_ovens = queue.Queue()
    self.pizzas_in_preparation = {}
    self.devices = {
      enums.DeviceType.ROBOT_BEFORE_OVEN.value: {},
      enums.DeviceType.OVEN.value: {},
      enums.DeviceType.ROBOT_AFTER_OVEN.value: {}
    }

    for _ in range(num_pizzas_to_prepare):
      self.queue_robots_before_ovens.put(Pizza())

    self.open()

  def open(self):
    """Starts the websocket server."""

    start_server = websockets.serve(self.handler, "localhost", 8765)
    loop = asyncio.get_event_loop()
    loop.set_debug(True)
    loop.run_until_complete(start_server)
    loop.run_until_complete(self.producer_handler())
    loop.run_forever()

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
      pizza = self.pizzas_in_preparation[pizza_data['id']]
      if ((pizza.status == enums.PizzaStatus.NOT_STARTED.value 
           and pizza_data['status'] == enums.PizzaStatus.IN_PREPARATION.value) or
          (pizza.status == enums.PizzaStatus.IN_PREPARATION.value 
           and pizza_data['status'] == enums.PizzaStatus.WAITING_FOR_OVEN.value) or
          (pizza.status == enums.PizzaStatus.WAITING_FOR_OVEN.value 
           and pizza_data['status'] == enums.PizzaStatus.OVEN_OPEN.value) or
          (pizza.status == enums.PizzaStatus.OVEN_OPEN.value 
           and pizza_data['status'] == enums.PizzaStatus.IN_OVEN.value) or
          (pizza.status == enums.PizzaStatus.IN_OVEN.value 
           and pizza_data['status'] == enums.PizzaStatus.COOKING.value) or
          (pizza.status == enums.PizzaStatus.COOKING.value 
           and pizza_data['status'] == enums.PizzaStatus.READY_TO_PACK.value)):
        pizza.status = pizza_data['status']
      
      self.pizzas_in_preparation[pizza.id] = pizza

    self.devices[data['type']][data['id']].status = data['status']

  async def producer_handler(self):
    """Handles outgoing messages queue."""

    while True:
      while not self.queue_messages.empty():
        websocket, message = self.queue_messages.get()
        await self.send(websocket, message)
      await asyncio.sleep(.5)
  
  async def cooking_handler(self, websocket, path, device):
    """Routes device."""

    while True:
      pizzas = [(p.id, p.status) for p in self.pizzas_in_preparation.values()]
      type = device.type
      if type == enums.DeviceType.ROBOT_BEFORE_OVEN.value:
        self.cooking_handler_robot_before_oven(device)
      elif type == enums.DeviceType.OVEN.value:
        self.cooking_handler_oven(device)
      elif type == enums.DeviceType.ROBOT_AFTER_OVEN.value:
        self.cooking_handler_robot_after_oven(device)
      await asyncio.sleep(1)

  def cooking_handler_robot_before_oven(self, device):
    if device.status == enums.RobotBeforeOvenStatus.IDLE.value:
      pizza = self.queue_robots_before_ovens.get()
      if pizza:
        pizza.robot_before_over_id = device.id
        self.pizzas_in_preparation[pizza.id] = pizza
        self.devices[device.type][device.id].status = enums.RobotBeforeOvenStatus.PREPARING.value
        self.devices[device.type][device.id].pizza_id = pizza.id
        message = {
          'pizza_id': pizza.id,
          'action': enums.RobotBeforeOvenEvent.PREPARE.value
        }
        self.queue_messages.put((device.websocket, message))
    elif device.status == enums.RobotBeforeOvenStatus.WAITING_FOR_OVEN.value:
      pizzas_oven_open = [
        p for p in self.pizzas_in_preparation.values()
        if p.status == enums.PizzaStatus.OVEN_OPEN.value
      ]
      if pizzas_oven_open:
        for pizza in pizzas_oven_open:
          if pizza.id == device.pizza_id:
            message = {
              'action': enums.RobotBeforeOvenEvent.PUT_IN_OVEN.value
            }
            self.queue_messages.put((device.websocket, message))
            break

  def cooking_handler_oven(self, device):
    if device.status == enums.OvenStatus.IDLE.value:
      pizzas_waiting = [
        p for p in self.pizzas_in_preparation.values()
        if p.status == enums.PizzaStatus.WAITING_FOR_OVEN.value
      ]
      print('pizzas_waiting')
      print(pizzas_waiting)
      for pizza in pizzas_waiting:
        if not pizza.oven_id:
          pizza.oven_id = device.id
          self.pizzas_in_preparation[pizza.id] = pizza
          self.devices[device.type][device.id].pizza_id = pizza.id
          message = {
            'pizza_id': pizza.id,
            'action': enums.OvenEvent.OPEN.value
          }
          self.queue_messages.put((device.websocket, message))
          break
    elif device.status == enums.OvenStatus.OPEN.value:
      pizzas_in_oven = [
        p for p in self.pizzas_in_preparation.values()
        if p.status == enums.PizzaStatus.IN_OVEN.value
      ]
      if pizzas_in_oven:
        for p in pizzas_in_oven:
          if device.pizza_id == p.id:
            message = {
              'action': enums.OvenEvent.COOK.value
            }
            self.queue_messages.put((device.websocket, message))
            break

  def cooking_handler_robot_after_oven(self, device):
    return

  async def send(self, websocket, message):
    """Sends message"""

    await websocket.send(json.dumps(message))