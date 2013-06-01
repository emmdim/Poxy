import sys
from pox.core import core
from pox.lib.revent import *
import threadedserver

"""
This module uses the threadedserver to communicate with other controllers.

The main idea in this module would be to overwrite the _handle_PacketIn
function or only some specific message handlers (for example handlers of
HELLO). The basis for this can be the pox/openflow/of_01.py

"""


log = core.getLogger()

class Proxy (object) :
    "A simple proxy"
    
    myserver = None


    def __init__(self) :
        log.debug("After register")
        self.myserver = threadedserver.MyServer()
        log.info("Server started")
        self.myserver.server.addListeners(self)
        while True:
            pass
    
    def _handle_MessageArrived (self, event):
        log.debug('Incoming message: '+event.msg)
        self.myserver.send(event.src,event.msg)


def launch ():
    core.registerNew(Proxy)
