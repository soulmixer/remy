
from enum import Enum

class WebSocket(Enum):
  URI = 'ws://localhost:8765'

class DeviceType(Enum):
  OVEN = 'OVEN'
  ROBOT_BEFORE_OVEN = 'ROBOT_BEFORE_OVEN'
  ROBOT_AFTER_OVEN = 'ROBOT_AFTER_OVEN'

class DeviceStatus(Enum):
  IDLE = 'IDLE'
  WORKING = 'WORKING'

class PizzaStatus(Enum):
  NOT_STARTED = 'NOT STARTED'
  IN_PREPARATION = 'IN PREPARATION'
  WAITING_FOR_OVEN = 'WAITING_FOR_OVEN'
  OVEN_OPEN = 'OVEN_OPEN'
  IN_OVEN = 'IN_OVEN'
  COOKING = 'COOKING'
  READY_TO_PACK = 'READY_TO_PACK'

class RobotBeforeOvenStatus(Enum):
  IDLE = 'IDLE'
  PREPARING = 'PREPARING'
  WAITING_FOR_OVEN = 'WAITING_FOR_OVEN'
  PIZZA_IN_OVEN = 'PIZZA_IN_OVEN'

class RobotBeforeOvenEvent(Enum):
  WAIT = 'WAIT'
  PREPARE = 'PREPARE'
  PUT_IN_OVEN = 'PUT_IN_OVEN'

class OvenEvent(Enum):
  OPEN = 'OPEN'
  COOK = 'COOK'
  CLOSE = 'CLOSE'

class OvenStatus(Enum):
  IDLE = 'IDLE'
  OPEN = 'OPEN'
  COOKING = 'COOKING'
  WAITING_FOR_ROBOT_AFTER = 'WAITING_FOR_ROBOT_AFTER'

class RobotAfterOvenEvent(Enum):
  PICK_PIZZA = 'PREPARE_PIZZA'