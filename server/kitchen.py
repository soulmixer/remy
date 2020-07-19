import asyncio
from devices.factory import DeviceFactory
import sys
sys.path.append('..')
from client import enums
import json
from orders.orders import Orders
import queue
import websockets


class Kitchen(object):
  """The Kitchen class.

  Attributes:
    orders: An Orders instance, the orders being prepared.
    queue_outgoing_messages: A queue, the messages to send.
    devices: A dict, the list of registered devices. 
    loop: The event loop.
  """

  def __init__(self):
    self.orders = Orders()
    self.queue_outgoing_messages = queue.Queue()
    self.devices = {
      enums.DeviceType.ROBOT_BEFORE_OVEN.value: {},
      enums.DeviceType.OVEN.value: {},
      enums.DeviceType.ROBOT_AFTER_OVEN.value: {}
    }
    self.loop = None

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

    device = DeviceFactory.create(type, id, status, websocket) 

    self.devices[type][id] = device

    consumer_task = asyncio.create_task(
      self.consumer_handler(websocket))
    cooking_task = asyncio.create_task(
      self.cooking_handler(device))
    done, pending = await asyncio.wait(
      [consumer_task, cooking_task],
      return_when = asyncio.FIRST_COMPLETED,
    )

    for task in pending:
      task.cancel()

  async def consumer_handler(self, websocket):
    """Handles websocket incoming messages."""

    async for message in websocket:
      await self.consumer(message)

  async def consumer(self, message):
    """Consumes message."""

    data = json.loads(message)
    pizza = data['pizza']
    if pizza['id']:
      self.orders.orders_in_preparation[pizza['id']].status = pizza['status']   

    device = self.devices[data['type']][data['id']]
    device.status = data['status']
    device.pizza_id = pizza['id']

    await asyncio.sleep(.5)

  async def producer_handler(self):
    """Handles outgoing messages queue."""

    while True:
      while not self.queue_outgoing_messages.empty():
        device, message = self.queue_outgoing_messages.get()
        await device.send_message(message)
      await asyncio.sleep(1)

      self.orders.log_orders_status()
  
  async def cooking_handler(self, device):
    """Cooking handler."""

    while True:
      await device.cooking_handler(self.orders, self.queue_outgoing_messages)
      await asyncio.sleep(.5)

  