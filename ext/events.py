from pox.core import core
from pox.lib.revent import *


"""
This is a class to declare all the custom events.

"""

log = core.getLogger()

class MessageArrived (Event):
    def __init__ (self, msg=None) :
        Event.__init__(self)
        #log.debug("Inside Event")
        self.msg = msg

