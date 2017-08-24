from pushbullet import Pushbullet
import logging
import sys

def setup_custom_logger(name):
    formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    handler = logging.FileHandler('log.txt', mode='w')
    handler.setFormatter(formatter)
    screen_handler = logging.StreamHandler(stream=sys.stdout)
    screen_handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    logger.addHandler(screen_handler)
    return logger

class Notification(object):

   def __init__(self, keyfile):
      with open(keyfile) as f:
         self.pb = Pushbullet(f.readline().strip())

   def notify(self, subject, msg):
      self.pb.push_note(subject, msg)
