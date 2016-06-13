import time

from acss.udp.daemon import ACUDPDaemon
from acss.cli import config


def run(settings):
    session = ACUDPDaemon(settings)

    while 1:
        session.update()
        time.sleep(0.005)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.stderr.write("Usage: %s <config_file>\n" % (sys.argv[0],))
        sys.exit(1)

    run(config.merge(sys.argv[1]))
