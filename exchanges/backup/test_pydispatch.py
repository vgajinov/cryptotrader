from pydispatch import dispatcher
import time

# class Handlers():
#    def handler1(sender, data):
#       print('Handler 1 : %s' % data)
#
#    def handler2(sender, data):
#       print('Handler 2 : %s' % data)


# ho1 = Handlers()
# ho2 = Handlers()
# ho3 = Handlers()
#
# dispatcher.connect(ho1.handler1, signal='test', sender='snd')
# dispatcher.connect(ho2.handler2, signal='test', sender='snd')
# dispatcher.connect(ho3.handler1, signal='test', sender='snd')


def handler1(sender, data):
   print('Handler 1 : %s' % data)


def handler2(sender, data):
   print('Handler 2 : %s' % data)

func1=handler1
func2=handler2
func3=handler1

def handler3(sender, data):
   handler1(sender, data)

dispatcher.connect(handler3, signal='test', sender='snd')
dispatcher.connect(func2, signal='test', sender='snd')
dispatcher.connect(func3, signal='test', sender='snd')

dispatcher.send(signal='test', sender='snd', data='Got some data')

time.sleep(2)