import sys
from pox.core import core
from pox.lib.revent import *
import async



"""
This module lies in the middle of the asynchornous connection object of
async.py and the higher level application

It gives the abstraction of a Proxy between the switch and the remote
controller.

#The main idea in this module would be to overwrite the _handle_PacketIn
#function or only some specific message handlers (for example handlers of
#HELLO). The basis for this can be the pox/openflow/of_01.py

"""

# To create and send the test ofp packet
import pox.openflow.libopenflow_01 as of

log = core.getLogger()

class Proxy (object) :
    "A simple proxy"
    
    myserver = None
    controller = None
    
    def _handle_ProxyMessageArrived (self, event):
        log.debug('Incoming message: '+event.msg)
        #self.send(event.msg)

    def send(self,  msg):
        self.conn.send(msg)



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


    def __init__(self, msg = None, rcontroller=('127.0.0.1',6634)) :
        #log.debug('After register message:'+msg)
        print type(msg)
        self.conn = async.Conn(msg, rcontroller)
        log.info("Connection with remote Proxy initiated")
        self.conn.client.addListeners(self)
        # Example to test send
        #msg = of.ofp_hello()
        #print msg
        #self.send(msg)
    

def launch ():
    core.registerNew(Proxy)
