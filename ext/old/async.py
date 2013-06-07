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


log = core.getLogger()



### TCP Socket Client using asyncore module

class Client(asyncore.dispatcher, EventMixin):

    # Declaring the event
    _eventMixin_events = set([
              ProxyMessageArrived,
    ])
    
    def __init__(self, server=("127.0.0.1",6634)):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        #self.setsockopt( socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        #self.setsockopt( socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.connect( (server) )
        self.buffer = ''

    def handle_connect(self):
        pass

    def handle_close(self):
        self.close()

    def handle_read(self):
        msg = self.recv(2048)
        log.debug('READ')
        self.raiseEvent(ProxyMessageArrived,msg)

    def writable(self):
        return (len(self.buffer) > 0)

    def handle_write(self):
        #log.debug('handle_write'+self.buffer)
        sent = self.send(self.buffer)
        if sent != len(self.buffer):
                log.debug("Didn't send complete buffer.")
        log.debug('The buffer is ' + self.buffer)
        self.buffer = ''
        #self.buffer = self.buffer[sent:]
   

### Actuall connection class

class Conn :

    def send (self, msg) :
      self.client.buffer = msg
    
    def __init__ (self, msg=None, rcontroller=('127.0.0.1',6634)):
        self.client = Client(rcontroller)
        log.debug("Client listening 0")
        #msg1 = msg
        #log.debug('The hello message: '+msg1)
        self.send(msg)

        # Put the asyncore in a loop
        t=threading.Thread(target=asyncore.loop())
        log.debug("Client listening 1")
        t.setDaemon(True) # don't hang on exit
        t.start()
        #print 'Server loop running in process:', threading.current_thread()



### For launching through pox.py in command line
def launch ():
        core.registerNew(Conn)
