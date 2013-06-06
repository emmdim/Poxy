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
import pox.openflow.libopenflow_01 as of
from pox.openflow.util import make_type_to_unpacker_table
unpackers = make_type_to_unpacker_table()


import pox
from pox.openflow.libopenflow_01 import *


log = core.getLogger()



### TCP Socket Client using asyncore module
from pox.lib.recoco.recoco import *

class Client(Task, EventMixin):

    # Declaring the event
  _eventMixin_events = set([
        ProxyMessageArrived,
  ])
    
  def __init__ (self, address = ('127.0.0.1',6634)):
    Task.__init__(self)
    self.address = address
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    self.buf = ''
    self.barrierxid = 0
    self.sock.connect(self.address)
    # This is not needed since I start this client when I already
    # receive feautres of switches :-P
    #core.addListener(pox.core.GoingUpEvent, self.start_event_loop)
    log.debug('Proxy in Loop 1')
    self.start_event_loop()

  def run (self):
    log.debug("Connected to remote controller")
    # List of open sockets/connections to select on
    sockets = [self.sock]
    
    while True:
      try:
        log.debug('Core is running')
        con = None
        rlist, wlist, elist = yield Select(sockets, [], [],1)
        if len(rlist) == 0 and len(wlist) == 0 and len(elist) == 0:
            if not core.running: break

        for con in rlist:
            self.read()
            
      except exceptions.KeyboardInterrupt:
        break
    log.debug("No longer listening for connections")

    #pox.core.quit()

  def read(self):
    d = self.sock.recv(2048)
    log.debug('Inside READ')
    if len(d) == 0:
        log.debug('Inside FALSE')
        return False
    self.buf += d
    buf_len = len(self.buf)
    offset = 0
    while buf_len - offset >= 8:
        log.debug('In da loop')
        ofp_type = ord(self.buf[offset+1])
        msg_length = ord(self.buf[offset+2]) << 8 | ord(self.buf[offset+3])
        if buf_len - offset < msg_length: break
        new_offset,msg = unpackers[ofp_type](self.buf, offset)
        assert new_offset - offset == msg_length
        offset = new_offset
        log.info('In handle_read')
        log.info(msg)
        #if isinstance(msg, pox.openflow.libopenflow_01.ofp_barrier_request):
         #   log.debug('Is instance with XID')
         #   log.debug(msg.xid)
         #   self.barrierxid = msg.xid
        log.debug('Before Event')
        self.raiseEvent(ProxyMessageArrived,msg)

    if offset != 0:
        self.buf = self.buf[offset:]

  def send(self,msg):
    log.debug('handle_write'+msg)
    sent = self.sock.send(msg)
        #if sent != len(self.buffer):
        #        log.debug("Didn't send complete buffer.")
        #log.debug('The buffer is ' + self.buffer)
        #self.buffer = self.buffer[sent:]
        #self.buffer = self.buffer[sent:]
  
  # Not a handler anymore
  #def start_event_loop(self, event):
  def start_event_loop(self):
      #t=threading.Thread(target=Task.start(self))
      #t.setDaemon(True) # don't hang on exit
      #t.start()
    log.debug('Proxy in Loop 2')
    Task.start(self)

### Actuall connection class

class Conn() :

    def send (self, msg) :
      self.client.send(msg)
      log.debug('Message Sent')

    def start(self,msg):
        self.send(msg)
        #self.client.boot()
        #t=threading.Thread(target=self.client.start())
        #t.setDaemon(True) # don't hang on exit
        #t.start()
        
        log.debug('Client Started')

    def __init__ (self, rcontroller=('127.0.0.1',6634)):
        #super(Conn,self).__init__()
        self.rcontroller = rcontroller
        self.client = Client(self.rcontroller)
        log.debug("Client listening 0")
        #self.msg = msg
        #log.debug('The hello message: '+msg1)
        #asyncore.loop()
        #self.send(msg)



### For launching through pox.py in command line
def launch ():
        core.registerNew(Conn)
