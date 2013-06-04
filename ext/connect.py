import select
import threading
import socket
from events import *

from pox.core import core
from pox.lib.revent import *
from pox.lib.revent.revent import EventMixin

"""
This is the main server component. It implements a UDPServer which 
1) raises a MessageArrived event when a new message appears.
2) provides a send function 

"""

import pox.openflow.libopenflow_01 as of


log = core.getLogger()
### SERVER



class Client(EventMixin):

    # Declaring the event
    _eventMixin_events = set([
              ProxyMessageArrived,
    ])


    def connect(self) :
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.connect(self.server)
        return sock

    def listen(self,) :
        sock = self.sock
        while True:
            #log.debug("going to listen")
            rd,wr,er = select.select([sock],[],[],100)
            for s in rd:
                if s is sock:
                    msg = s.recv(1024)
                    #log.debug(msg)
                    self.raiseEvent(ProxyMessageArrived,msg)
                else:
                    log.debug("received empty message")
                #log.debug("Out of the loop almost")

    def send(self, msg= None) :
        self.sock.send(msg)


    def __init__ (self, server=('127.0.0.1',6634)):
        self.server = server
        self.sock = self.connect()
        #self.listen(self.sock)


# ACTUAL CLASS

class Test :
    
    server = None
    t = None

    def __init__ (self) :

        address = ('127.0.0.1', 6634) # let the kernel give us a port
        client = Client(address)
        msg = of.ofp_features_request().show()
        print msg
        client.send(msg)
        t = threading.Thread(target=client.listen())
        t.setDaemon(True) # don't hang on exit
        t.start()
        print 'Server loop running in process:', threading.current_thread()

    def stop (self):
        self.t.stop()

#    def send (self,dst, msg) :
#        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#        s.sendto(msg, dst)
#        s.close()

def launch ():
    core.registerNew(Test)

