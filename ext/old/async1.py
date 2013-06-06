import threading
import asyncore, socket

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

class Client(asyncore.dispatcher, EventMixin):

    # Declaring the event
    _eventMixin_events = set([
              ProxyMessageArrived,
    ])
    
    def __init__(self, server=("127.0.0.1",6634)):
        asyncore.dispatcher.__init__(self)
        self.buffer = ''
        
        self.buf = ''
        self.barrierxid = 0
        for res in socket.getaddrinfo('127.0.0.1',6634, socket.AF_UNSPEC,socket.SOCK_STREAM):
                af, socktype, proto, canonname, sa = res
        #self.create_socket(af,socktype,proto)
        self.create_socket(af,socktype)
        #self.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR, 1)
        self.set_reuse_addr()
        self.connect(sa)
        #self.setsockopt( socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        #self.connect( (server) )

    def handle_connect(self):
        pass

    def handle_close(self):
        self.close()

    def handle_read(self):
        d = self.recv(2048)
        if len(d) == 0:
            return False
        self.buf += d
        buf_len = len(self.buf)
        offset = 0
        while buf_len - offset >= 8:
            ofp_type = ord(self.buf[offset+1])
            msg_length = ord(self.buf[offset+2]) << 8 | ord(self.buf[offset+3])
            if buf_len - offset < msg_length: break
            new_offset,msg = unpackers[ofp_type](self.buf, offset)
            assert new_offset - offset == msg_length
            offset = new_offset
            log.info('In handle_read')
            log.info(msg)
            if isinstance(msg, pox.openflow.libopenflow_01.ofp_barrier_request):
                #log.debug('Is instance with XID')
                #log.debug(msg.xid)
                self.barrierxid = msg.xid
        log.debug('Before Event')
        self.raiseEvent(ProxyMessageArrived,msg)

    def writable(self):
        return (len(self.buffer) > 0)

    def readable(self):
        return True

    def handle_write(self):
        #log.debug('handle_write'+self.buffer)
        sent = self.send(self.buffer)
        if sent != len(self.buffer):
                log.debug("Didn't send complete buffer.")
        log.debug('The buffer is ' + self.buffer)
        self.buffer = self.buffer[sent:]
        #self.buffer = self.buffer[sent:]

    def send_data(self, msg):
        self.bugger = msg

### Actuall connection class

class Conn() :

    def send (self, msg) :
      self.client.send_data(msg)
    
    def __init__ (self, msg=None, rcontroller=('127.0.0.1',6634)):
        #super(Conn,self).__init__()
        self.client = Client(rcontroller)
        log.debug("Client listening 0")
        self.msg = msg
        #log.debug('The hello message: '+msg1)
        #asyncore.loop()
        self.send(msg)

    def start(self) :
        #pass
        #asyncore.loop(1)
        # Put the asyncore in a loop
        t=threading.Thread(target=asyncore.loop(0.5))
        #self.send(self.msg)
        log.debug("Client listening 1")
        
        t.setDaemon(True) # don't hang on exit
        t.start()
        #log.debug('I am not stuck')
        #print 'Server loop running in process:', threading.current_thread()



### For launching through pox.py in command line
def launch ():
        core.registerNew(Conn)
