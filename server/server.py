import asyncio
import kitchen
import logging
import sys
import websockets

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

def run():
  # brew services start rabbitmq
  
  dark_kitchen = kitchen.Kitchen()
  """
  try:
    dark_kitchen = kitchen.Kitchen()
  except KeyboardInterrupt:
    logging.info('Process interrupted')
  finally:
    logging.info('Successfully shutdown the Mayhem service.')
  """

if __name__ == '__main__':
  run()