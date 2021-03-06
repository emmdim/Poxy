import threading
import SocketServer
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


# OVERRIDES

class ThreadedEchoRequestHandler(SocketServer.BaseRequestHandler):

    data = None
    src = None

    def handle(self):
        # Echo the back to the client
        self.data = self.request[0].strip()
        socket = self.request[1]
        self.src = self.client_address
        log.debug(socket)
        #TCP data = self.request.recv(1024)
        cur_thread = threading.current_thread()
        #response = '%s: %s' % (cur_thread, self.data)
        #socket.sendto(response, self.client_address)
        # TCP self.request.send(response)


# EventMixin is also made a supercalls to be bale to raise the event
class ThreadedEchoServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer,
        EventMixin):
    
    # Declaring the event
    _eventMixin_events = set([
              ProxyMessageArrived,
    ])
    
    # Overriding the finish_request function of SocketServer.BaseServer
    def finish_request(self, request, client_address):
        """Finish one request by instantiating RequestHandlerClass."""
        obj = self.RequestHandlerClass(request, client_address, self)
        # Raise the event
        self.raiseEvent(ProxyMessageArrived, obj.src,  obj.data)


# ACTUAL CLASS

class MyServer :
    
    server = None
    t = None

    def __init__ (self) :

        address = ('127.0.0.1', 6640) # let the kernel give us a port
        # TCP server = ThreadedEchoServer(address, ThreadedEchoRequestHandler)
        self.server = ThreadedEchoServer(address, ThreadedEchoRequestHandler)
        #ip, port = server.server_address # find out what port we were given
        print 'Server running at ip: %s and port %s' % (address)
        t = threading.Thread(target=self.server.serve_forever)
        t.setDaemon(True) # don't hang on exit
        t.start()
        print 'Server loop running in process:', threading.current_thread()
        print self.server.socket
        self.server.socket.connect(('127.0.0.1',6634))
        msg = of.ofp_features_request().show()
        print msg
        self.server.socket.send(msg)

    def stop (self):
        self.t.stop()

    def send (self,dst, msg) :
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.sendto(msg, dst)
        s.close()


### CLIENT


class MyClient :

    def __init__ (self,ip= "127.0.0.1", port= 6640) :
        # Connect to the server
        #TCP s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Send the data
        message = 'Hello, world'
        print 'Sending : "%s"' % message
        len_sent = s.sendto(message, (ip,port))

        # Receive a response
        response = s.recv(1024)
        print 'Received: "%s"' % response

        # Clean up
        s.close()
