import time
import sys
import logging

from acss.udp.daemon import ACUDPDaemon
from acss.cli import config
import acudpclient.exceptions
import acudpclient.packets

log = logging.getLogger('acss_udp')

def run():
    if len(sys.argv) != 2:
        sys.stderr.write("Usage: %s <config_file>\n" % (sys.argv[0],))
        sys.exit(1)

    session = ACUDPDaemon(config.merge(sys.argv[1]))
    session.client.enable_realtime_report(0)
    current_time = 0
    log.info("acss_udp start")
    while 1:
        if time.time() - current_time >= 15.0:
            session.client.get_session_info()
            current_time = time.time()
        try:
            event = session.update()
        except acudpclient.exceptions.NotEnoughBytes:
            pass
        except Exception, e:
            log.error(e)
            raise
        else:
            print event

        time.sleep(0.001)
