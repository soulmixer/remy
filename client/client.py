from devices import oven
from devices import robots
import time
import asyncio

async def run():
  devices = []
  devices_late = []

  devices.append(robots.RobotBeforeOven('Robot Before 1'))
  devices.append(robots.RobotBeforeOven('Robot Before 2'))
  devices.append(robots.RobotBeforeOven('Robot Before 3'))
  devices.append(robots.RobotBeforeOven('Robot Before 4'))

  devices.append(oven.Oven('Oven 1'))
  devices_late.append(oven.Oven('Oven 2'))
  devices_late.append(oven.Oven('Oven 3'))
  devices_late.append(oven.Oven('Oven 4'))

  devices.append(robots.RobotAfterOven('Robot After 1'))
  devices.append(robots.RobotAfterOven('Robot After 2'))
  devices.append(robots.RobotAfterOven('Robot After 3'))
  devices.append(robots.RobotAfterOven('Robot After 4'))

  try:
    for d in devices:
      d.start()

    await asyncio.sleep(10)
  
    for d in devices_late:
      d.start()
  except KeyboardInterrupt:
    logging.info('Process interrupted')
  finally:
    logging.info('Successfully shutdown the devices service.')

if __name__ == '__main__':
  asyncio.run(run())