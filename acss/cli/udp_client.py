from acss.udp.session import ACUDPSession

def run():
    session = ACUDPSession()

    while 1:
        session.update()

if __name__ == '__main__':
    run()
