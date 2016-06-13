import socket
import sys
import time
import struct
import logging

from acss.udp.client import ACUDPClient4


logging.basicConfig(level=logging.INFO)
log = logging.getLogger("acss_udp")

"""
Simulate AC bytes
"""
def client():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    server_address = ('localhost', 10000)
    f = open('ac_out', 'rb')
    try:
        bytes_ = 0
        while 1:
            start_pos = f.tell()
            log.debug("current file position %d" % (f.tell(),))
            event = ACUDPClient4.consume_event(f)
            size = f.tell()-start_pos
            f.seek(-size, 1)
            data = f.read(size)
            log.debug("Sending %s" % (
                ':'.join([b.encode('hex') for b in data]),)
            )
            sent = sock.sendto(data, server_address)

    finally:
        print >>sys.stderr, 'closing socket'
        sock.close()


client()
