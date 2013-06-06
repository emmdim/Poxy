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
        msg = event.msg
        
        # Check if the message is a hello package and reply
        if isinstance(msg,of.ofp_hello) :
            self.send(msg.pack())
        
        # Check if the message is a features request 
        # and see if we got already the features from
        # the actual switch in order to reply
        if isinstance(msg,of.ofp_features_request) :
            self.send((self.features).pack())

        # Check if the message is a Barrier in and reply
        if isinstance(msg, of.of_barrier_request) :
            newmsg = of.ofp_barrier_reply()
            nemsg.xid = msg.xid
            self.send(newmsg.pack)

        self.q.put(msg)
        log.debug('Incoming message: '+msg.show())
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


   def start(self,features):
       self.conn = async2.Conn(rcontroller)
       self.conn.client.addListeners(self)
       self.features = features
       #send starting hello
       msg = of.ofp_hello()
       self.conn.start(msg.pack())


    def __init__(self,  rcontroller=('127.0.0.1',6634)) :
        #log.debug('After register message:'+msg)
        #print type(msg)
        self.q = Queue.Queue()
        self.conn = None
        self.features = None
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
