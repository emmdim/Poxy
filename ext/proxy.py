import sys
from pox.core import core
from pox.lib.revent import *
import async2
import events
import Queue


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
        log.debug('In Handle')
        self.q.put(event.msg)
        log.debug('Incoming message: '+event.msg.show())
        #self.send(event.msg)


    def send(self,  msg):
        self.conn.send(msg)


    def read(self) :    
        #log.debug('Inside read')
        #log.debug(self.q.qsize())
        #if self.q.empty(): return ''
        while self.q.empty(): pass
        msg = self.q.get()
        log.debug('Read msg: '+ msg.show())
        return msg


 #   def start(self,msg):
 #       self.conn.start(msg)


    def __init__(self,  rcontroller=('127.0.0.1',6634)) :
        #log.debug('After register message:'+msg)
        #print type(msg)
        self.q = Queue.Queue()
        self.conn = async2.Conn(rcontroller)
        self.conn.client.addListeners(self)
        #self.conn.start()
        log.info("Connection with remote Controller initiated")
        # Example to test send
        #msg = of.ofp_hello()
        #print msg
        #self.send(msg)


# ProxyInWrapper
#class Proxy (object):
#
#    def read(self):
#        msg = self.pro.read()
#        while msg == '' : 
#            msg = self.pro.read()
#        return msg
#
#    def send(self,msg ):
#        self.pro.send(msg)
#
#    def start(self,msg) :
#        self.pro.start(msg)
#
#    def __init__(self, rcontroller=('127.0.0.1',6634)):
#        self.pro = ProxyIn(rcontroller)



def launch ():
    core.registerNew(Proxy)
