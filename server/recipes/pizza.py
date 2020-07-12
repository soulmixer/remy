import uuid
import sys
sys.path.append('..')
from client import enums

class Pizza(object):
  """Pizza"""

  def __init__(self):
    self.id = str(uuid.uuid4())
    self.status = enums.PizzaStatus.NOT_STARTED.value
    self.robot_before_over_id = None
    self.oven_id = None
    self.robot_after_oven_id = None
    