import socket
import sys
import time
import struct
import logging

from test_udp_proto import ACUDPServer4


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
            event = ACUDPServer4.consume_event(f)
            size = f.tell()-start_pos
            f.seek(-size, 1)
            data = f.read(size)
            log.debug("Sending %s" % (
                ':'.join([b.encode('hex') for b in data]),)
            )
            # HACK: if sending all at once, localhost, server will discard bytes
            for c in data:
                sent = sock.sendto(c, server_address)
                time.sleep(0.0001)
    finally:
        print >>sys.stderr, 'closing socket'
        sock.close()


client()
