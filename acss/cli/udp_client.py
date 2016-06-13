import time
import sys

from acss.udp.daemon import ACUDPDaemon
from acss.cli import config


def run():
    if len(sys.argv) != 2:
        sys.stderr.write("Usage: %s <config_file>\n" % (sys.argv[0],))
        sys.exit(1)

    session = ACUDPDaemon(config.merge(sys.argv[1]))

    while 1:
        print session.update()
