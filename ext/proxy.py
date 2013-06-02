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
    controller = None
    
    def _handle_ProxyMessageArrived (self, event):
        log.debug('Incoming message: '+event.msg)
        self.send(self.controller,event.msg)

    def send(self, dst, msg):
        self.myserver.send(dst,msg)



    def logic ():
        import pox.openflow.libopenflow_01 as of
        from pox.lib.util import dpidToStr

        def _handle_ConnectionUp (event):
            msg = of.ofp_flow_mod()
            msg.actions.append(of.ofp_action_output(port = of.OFPP_FLOOD))
            event.connection.send(msg)
            log.info("Hubifying %s", dpidToStr(event.dpid))

        core.openflow.addListenerByName("ConnectionUp", _handle_ConnectionUp)
        log.info("Hub running.")


    def __init__(self, controller=('127.0.0.1',6634)) :
        self.controller = controller
        log.debug("After register")
        self.myserver = threadedserver.MyServer()
        log.info("Server started")
        self.myserver.server.addListeners(self)
   #     while True:
   #         pass
    

def launch ():
    core.registerNew(Proxy)
