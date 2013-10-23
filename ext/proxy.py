import sys
from pox.core import core
from pox.lib.revent import *
import async
import events
import Queue


"""
This module lies in the middle of the asynchornous connection object of
async.py and the basic POX functionality. It gives the abstraction of a 
Proxy between the switch and the remote controller.

On the one hand it receives messages from the remote controller and 
sends them to the switch (through the local controller connection).
On the other hand, it receives messages (through the local controller
connection) and forwards them to the remote controller.
"""

# To create and send the test ofp packet
import pox.openflow.libopenflow_01 as of

# For debugging
log = core.getLogger()

""" 
    Mesage Handlers
    
    Handlers of the messages coming from the local controller.
    (raised from the pox environment core.openflow)
"""


def handle_hello(proxy):
    log.debug('RECEIVED HELLO')

def handle_features_request(proxy):
    log.debug('RECEIVED FEATURES REQUEST')
    proxy.send((proxy.switch.features).pack())

def handle_barrier_request(proxy,msg):
    log.debug('RECEIVED FEATURES REQUEST')
    newmsg = of.ofp_barrier_reply()
    newmsg.xid = msg.xid
    proxy.send(newmsg.pack())

def handle_flow_mod(proxy,msg):
    proxy.switch.send(msg)
    log.debug('RECEIVED FLOW MOD')



class Proxy (object) :
    """ 
    The proxy
    """
    myserver = None # Is it needed?
    controller = None # Is it needed?

    # Catch incoming message from remote controller
    def _handle_RemoteMessageArrived (self, event):
        log.debug('In Handle')
        msg = event.msg
        
        # Check what OFP message it is
        # In could be a generic dispatcher but since for
        # now we are implementing only a few of the messages
        # it cannot be like that.
        #TODO In the far future add all the message handlers
        # above to make it more complet.

        # hello
        if isinstance(msg,of.ofp_hello) : handle_hello(self)
        
        # features_request 
        if isinstance(msg,of.ofp_features_request) :
            handle_features_request(self)

        # barrier_request
        if isinstance(msg, of.ofp_barrier_request) :
            handle_barrier_request(self,msg)

        # flow_mod
        if isinstance(msg, of.ofp_flow_mod) : handle_flow_mod(self,msg)

        #log.debug('Incoming message: ' + msg.show())

    #def _handle_ConnectionDown(self,event):


    # An abstraction to use the underlying socket
    def send(self,  msg):
        self.conn.send(msg)

    # Starting the connection with the remote controller 
    # and the underlying socket
    def start(self, switch, rcontroller= ('0.0.0.0',6634)):
        self.rcontroller = rcontroller
        # Create the underlying socket
        self.conn = async.Conn(rcontroller)
        # Listen to event coming from the socket and
        # are handled here
        self.conn.client.addListeners(self)
        # This is the POX connection object 
        self.switch = switch #where is this used???
        # Send starting hello
        msg = of.ofp_hello()
        self.conn.start(msg.pack())
        log.debug('SENT HELLO')

    # Initializing the proxy
    def __init__(self) :
        #log.debug('After register message:'+msg)
        #print type(msg)
        core.openflow.addListeners(self)
        self.rcontroller = None # Initialized  in start?
        self.conn = None # Initialized  in start?
        self.switch = None # Initialized  in start?
        #self.conn.start()
        log.info("Connection with remote Controller initiated")

    def stop(self):
        self.conn.stop()
        self.conn = None
        self.switch = None

def launch ():
    core.registerNew(Proxy)
