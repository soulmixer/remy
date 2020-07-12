import asyncio
import enums
import json
import logging
import sys
import threading
import uuid
import websockets

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

TASK_EXECUTON_TIME = 1

class Device(threading.Thread):
  """Device class.

  Attributes:
    id: A string, the id.
    type: A string, the type.
    name: A string, the name.
    status: A string, the status.
    websocket: An object, the websocket.
    pizza: An object, the pizza being prepared.
    loop: An object, the current event loop.
  """

  def __init__(self, type, name):
    super().__init__(target = self.thread)
    self.id = str(uuid.uuid4())
    self.type = type
    self.name = name
    self.status = enums.DeviceStatus.IDLE.value
    self.websocket = None
    self.pizza = {
      'id': None,
      'status': None
    }
    self.loop = None

  def thread(self):
    self.loop = asyncio.new_event_loop()
    asyncio.set_event_loop(self.loop)
    self.loop.run_until_complete(self.handler())

  async def handler(self):
    uri = enums.WebSocket.URI.value
    async with websockets.connect(uri) as websocket:
      self.websocket = websocket
      consumer_task = asyncio.create_task(
        self.consumer_handler(websocket))
      producer_task = asyncio.create_task(
        self.producer_handler(websocket))
      done, pending = await asyncio.wait(
        [consumer_task, producer_task],
        return_when = asyncio.FIRST_COMPLETED,
      )
      for task in pending:
        task.cancel()

  async def consumer_handler(self, websocket):
    """The websocket consumer handler."""

    raise NotImplementedError('You must implement the consumer_hander method.')

  async def producer_handler(self, websocket):
    """The websocket producer handler."""

    while True:
      await self.send()
      await asyncio.sleep(1)

  def log(self, message):
    """"Logs a message to stdout."""

    logging.info('%s -> %s' % (self.id, message))

  async def execute_task(self, name):
    """"Executes a task."""

    self.log('starting: ' + name)
    await asyncio.sleep(TASK_EXECUTON_TIME)
    self.log('finishing: ' + name)
       
  async def send(self, message = None):
    """Sends message"""

    data = {
      'id': self.id,
      'type': self.type,
      'status': self.status,
      'pizza': self.pizza,
      'message': message
    }

    print(self.status)
    await self.websocket.send(json.dumps(data))
    await asyncio.sleep(1)
