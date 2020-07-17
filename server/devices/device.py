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