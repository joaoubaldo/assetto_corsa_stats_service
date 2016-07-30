import socket
import os
import sys
import time
import struct
import logging
import threading
import unittest
from Queue import Queue
from Queue import Empty

import acudpclient.packets
from acudpclient.client import ACUDPClient
from acudpclient.packet_base import ACUDPPacket
from acudpclient.exceptions import NotEnoughBytes
from acss.udp.daemon import ACUDPDaemon


log = logging.getLogger("acss_udp")
log.setLevel(logging.DEBUG)


class TestUDPDaemon(unittest.TestCase):
    def test_daemon_event_parse(self):
        sent_events = Queue()

        def udp_worker():
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            server_address = ('localhost', 10000)
            raw_file = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                    'ac_out')
            f = open(raw_file, 'rb')
            while 1:
                start_pos = f.tell()
                log.debug("current file position %d" % (f.tell(),))
                try:
                    event = ACUDPPacket.factory(f)
                except NotEnoughBytes:
                    break
                size = f.tell()-start_pos
                f.seek(-size, 1)
                data = f.read(size)
                log.debug("Sending %s" % (
                    ':'.join([b.encode('hex') for b in data]),)
                )
                sent = sock.sendto(data, server_address)
                sent_events.put(data)
            sock.close()

        udp_thread = threading.Thread(target=udp_worker)
        daemon = ACUDPDaemon({
            'udp_bind_port': 10000,
            'udp_remote_port': 9999,
            'udp_remote_host': '127.0.0.1',
            'db_filename': ':memory:'
        })
        event_count = 0
        udp_thread.start()

        while 1:
            try:
                _ = sent_events.get(timeout=1.0)
            except Empty:
                pass

            try:
                daemon.update()
                event_count += 1
            except NotEnoughBytes:
                break

        udp_thread.join()
        self.assertEqual(event_count, 395)
