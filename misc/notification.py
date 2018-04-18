from pushbullet import Pushbullet
import logging
import sys

NOTIFY_LVL = 21
pb = None
logger = None

def setup_basic_logging(level = logging.INFO):
   formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

   # configure the handler to send log messages to file
   handler = logging.FileHandler('log.txt', mode='w')
   handler.setFormatter(formatter)
   # configure the handler to send log messages to screen
   screen_handler = logging.StreamHandler(stream=sys.stdout)
   screen_handler.setFormatter(formatter)
   # configure logging with the previously created handlers
   logging.basicConfig(level=level, handlers=[handler, screen_handler])

   global logger
   logger = logging.getLogger(__name__)

def notify(self, message, *args, **kws):
   pb.push_note("AutoTrader", message)
   logger.info(message)


def setup_remote_notification(keyfile):
   with open(keyfile) as f:
      global pb
      pb = Pushbullet(f.readline().strip())
   logging.addLevelName(NOTIFY_LVL, "NOTIFY")
   logging.Logger.notify = notify

