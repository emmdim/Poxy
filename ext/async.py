import threading
import socket
import select
import exceptions


from events import *

from pox.core import core
from pox.lib.revent import *
from pox.lib.revent.revent import EventMixin

"""
This is the main connection component. It implements a TCP socket which 
1) raises a ProxyMessageArrived event when a new message appears from
   the central controller.
2) provides a send function to send messages that arrive from the switch 

"""

# To create and send the test ofp packet
import pox
import pox.openflow.libopenflow_01 as of
from pox.openflow.util import make_type_to_unpacker_table
unpackers = make_type_to_unpacker_table()

# For debuggin purposes
log = core.getLogger()


# Contains the Task class
from pox.lib.recoco.recoco import *

import sys

class Client(Task, EventMixin):
  """
    TCP Socket Client using select module
    
    This class is actually a socket wrapper providing the basic functionalities
    of read and write to the socket with the advantage that it supports asynchronous 
    reading.
    The class is a Task as defined in the recoco POX library. Also it is a subclass
    of EventMixin as defined in the revent POX library, in order to throw
    Events.
    Sending can happen through this object but the info that there an incoming
    message is propagated with the help of the revent library from Pox. This is
    done to avoid polling.
    It throws the ProxyMessageArrived event when a message is read and parsed.
  """

  # Declaring the event that is thrown
  _eventMixin_events = set([
        ProxyMessageArrived,
  ])
    
  def __init__ (self, address = ('127.0.0.1',6634)):
    # Intializing Task
    Task.__init__(self)
    # Creating socket and connecting to remote host
    self.address = address
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    self.sock.connect(self.address)
    # buf is used for messages that are arrived in multiple PDUs
    self.buf = ''
    # This is not needed since I start this client when I already
    # receive feautres of switches :-P
    #core.addListener(pox.core.GoingUpEvent, self.start_event_loop)
    log.debug('Proxy in Loop 1')
    self.start_event_loop()

  # This function is like a main loop as defined in the Task class
  def run (self):
    log.debug("Connected to remote controller")
    # List of open sockets/connections to select on
    sockets = [self.sock]
    # The core of asynchronous reading
    while True:
      try:
        log.debug('Core is running')
        con = None
        rlist, wlist, elist = yield Select(sockets, [], [],5)
        if len(rlist) == 0 and len(wlist) == 0 and len(elist) == 0:
            if not core.running: break
        # If there are data for reading in the socket call the
        # read() function
        for con in rlist:
            self.read()
            
      except exceptions.KeyboardInterrupt:
        break
    log.debug("No longer listening for connections")


  def read(self):
    # Read the socket
    d = self.sock.recv(2048)
    log.debug('Inside READ')
    # Leave if read nothing
    if len(d) == 0:
        log.debug('Inside FALSE')
        return False
    # Add message to existing buffer om case it arrived in 
    # pieces
    self.buf += d
    buf_len = len(self.buf)
    # Bring the message in the format of  OF objects as they
    # are defined in the library pox/openflow/libopenflow_01
    offset = 0
    while buf_len - offset >= 8:
        log.debug('In da loop')
        ofp_type = ord(self.buf[offset+1])
        msg_length = ord(self.buf[offset+2]) << 8 | ord(self.buf[offset+3])
        if buf_len - offset < msg_length: break
        new_offset,msg = unpackers[ofp_type](self.buf, offset)
        assert new_offset - offset == msg_length
        offset = new_offset

        log.debug('In handle_read')
        log.info(msg)
        # msg here has the received message and it is propagated
        # to whoever listens the following event
        self.raiseEvent(ProxyMessageArrived,msg)

    # Check if there is more the previous message in the PDU
    if offset != 0:
        self.buf = self.buf[offset:]

  # Send a packet to the destination of the socket
  def send(self,msg):
    log.debug('handle_write'+msg)
    sent = self.sock.send(msg)
  
  # Start the Task
  # The Task.start(self) command does some internal initializations
  # and finally calls the above run() function.
  # Not a handler anymore
  #def start_event_loop(self, event):
  def start_event_loop(self):
    log.debug('Proxy in Loop 2')
    Task.start(self)

  def stop(self):
    self.sock.close()
    e = Exit()
    global defaultScheduler
    e.execute(self,defaultScheduler)
    #sys.exit(0)

class Conn() :
    """
    Connection class
    Provides a higher level view to the above which only
    can start and send messages.
    As said previously, since we want to avoid polling there is
    no read function but a raised event instead of that.
    """

    def send (self, msg) :
      self.client.send(msg)
      log.debug('Message Sent')

    def start(self,msg):
        self.send(msg)
        log.debug('Client Started')

    def __init__ (self, rcontroller=('127.0.0.1',6634)):
        #super(Conn,self).__init__()
        #self.pid = 
        self.rcontroller = rcontroller
        self.client = Client(self.rcontroller)
        log.debug("Client listening 0")



### For launching through pox.py in command line
def launch ():
        core.registerNew(Conn)
