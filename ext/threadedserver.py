import threading
import SocketServer


from pox.core import core
from pox.lib.revent import *
from pox.lib.revent.revent import EventMixin

"""
This is the main server component. It implements a UDPServer which 
1) raises a MessageArrived event when a new message appears.
2) provides a send function 

"""



log = core.getLogger()

class MessageArrived (Event):
    def __init__ (self, msg=None) :
        Event.__init__(self)
        log.debug("Inside Event")
        self.msg = msg


class ThreadedEchoRequestHandler(SocketServer.BaseRequestHandler):

    def handle(self):
        # Echo the back to the client
        data = self.request[0].strip()
        socket = self.request[1]
        #TCP data = self.request.recv(1024)
        cur_thread = threading.current_thread()
        response = '%s: %s' % (cur_thread, data)
        socket.sendto(response, self.client_address)
        # TCP self.request.send(response)
        return

class ThreadedEchoServer(SocketServer.ThreadingMixIn, SocketServer.UDPServer,
        EventMixin):
    
    _eventMixin_events = set([
              MessageArrived,
    ])
    
    def finish_request(self, request, client_address):
        """Finish one request by instantiating RequestHandlerClass."""
        self.raiseEvent(MessageArrived, "Message")
        self.RequestHandlerClass(request, client_address, self)




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

    def stop (self) :
        self.server.socket.close()
        self.t.stop()


class MyClient :

    def __init__ (self,ip= "127.0.0.1", port= 6640) :
        import socket
        # Connect to the server
        #TCP s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect((ip, port))

        # Send the data
        message = 'Hello, world'
        print 'Sending : "%s"' % message
        len_sent = s.send(message)

        # Receive a response
        response = s.recv(1024)
        print 'Received: "%s"' % response

        # Clean up
        s.close()
