
import queue
from recipes.pizza import Pizza

class Orders(object):
  """Orders."""

  def __init__(self):
    self.queue_orders = queue.Queue()
    self.orders_in_preparation = {}

    num_orders = 12
    for _ in range(num_orders):
      self.queue_orders.put(Pizza())

