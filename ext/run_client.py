import socket
import sys

from pox.core import core

log = core.getLogger()

# For testing purposes
class Client :
  "A simple UDP client"
  def __init__(self,server_ip="127.0.0.1",server_port=6640):
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = (server_ip, server_port)
    message = 'This is the message.  It will be repeated.'

    try:
        # Send data
        print >>sys.stderr, 'sending "%s"' % message
        sent = sock.sendto(message, server_address)
        # Receive response
        print >>sys.stderr, 'waiting to receive'
        data, server = sock.recvfrom(4096)
        print >>sys.stderr, 'received "%s"' % data

    finally:
        print >>sys.stderr, 'closing socket'
        sock.close()


def launch () :
    c = Client()
    core.register("myclient",c)
