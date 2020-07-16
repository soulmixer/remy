from devices import oven
from devices import robots
import time

def run():
  devices = []

  devices.append(robots.RobotBeforeOven('Robot Before 1'))
  devices.append(robots.RobotBeforeOven('Robot Before 2'))
  devices.append(robots.RobotBeforeOven('Robot Before 3'))
  devices.append(oven.Oven('Oven 1'))
  devices.append(oven.Oven('Oven 2'))
  devices.append(oven.Oven('Oven 3'))
  devices.append(robots.RobotAfterOven('Robot After 1'))
  devices.append(robots.RobotAfterOven('Robot After 2'))
  devices.append(robots.RobotAfterOven('Robot After 3'))

  for d in devices:
    d.start()
  for d in devices:
    d.join()

if __name__ == '__main__':
  run()