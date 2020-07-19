import sys
sys.path.append('..')
from client import enums
from devices.oven import Oven
from devices.robots import RobotBeforeOven, RobotAfterOven


class DeviceFactory(object):
  """DeviceFactory"""

  @staticmethod
  def create(type, id, status, websocket):
    if type == enums.DeviceType.ROBOT_BEFORE_OVEN.value:
      return RobotBeforeOven(id, type, status, websocket) 
    elif type == enums.DeviceType.OVEN.value:
      return Oven(id, type, status, websocket)   
    elif type == enums.DeviceType.ROBOT_AFTER_OVEN.value:
      return RobotAfterOven(id, type, status, websocket) 