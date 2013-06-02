from pox.core import core
from pox.lib.revent import *


"""
This is a class to declare all the custom events.

"""

log = core.getLogger()

class ProxyMessageArrived (Event):
    def __init__ (self, src=None,msg=None) :
        Event.__init__(self)
        #log.debug("Inside Event")
        self.src = src
        self.msg = msg
