from .client import ACUDPClient4
from .client import ACUDPListener

class ACUDPSession(ACUDPListener, object):
    def __init__(self, port=10000, remote_port=10001):
        self.server_name = ''
        self.cars = {}
        self.type = ''
        self.time = -1
        self.track = ''
        self.proto = -1
        self.laps = -1
        self.name = ''
        self.ambient_temp = -1
        self.elapsed_ms = -1
        self.track_temp = -1
        self.client = ACUDPClient4(port=10000, remote_port=10001)
        self.client.listen()
        self.client.subscribe(self)

    def update(self):
        event = self.client.read_event()
        return event

    def car_by_id(self, id_):
        for car in self.cars.itervalues():
            if car['car_id'] == id_:
                return car

    def on_ACSP_LAP_COMPLETED(self, event):
        pass

    def on_ACSP_NEW_SESSION(self, event):
        self.track = event['track_name']
        self.server_name = event['server_name']
        self.type = event['session_type']
        self.name = event['name']
        self.time = event['time']
        self.laps = event['laps']
        self.elapsed_ms = event['elapsed_ms']
        self.ambient_temp = event['ambient_temp']
        self.track_temp = event['track_temp']

    def on_ACSP_CHAT(self, event):
        pass

    def on_ACSP_NEW_CONNECTION(self, event):
        self.cars[event['driver_guid']] = event

    def on_ACSP_CONNECTION_CLOSED(self, event):
        if event['driver_guid'] in self.cars.keys():
            del self.cars[event['driver_guid']]

    def __repr__(self):
        d = self.__dict__
        d.update({'total_cars': len(self.cars),
        })
        return "<ACSession track=\"%(track)s\" session=\"%(name)s\" "\
            "server_name=\"%(server_name)s\" cars=%(total_cars)d time=%(time)d"\
            " laps=%(laps)d elapsed_ms=%(elapsed_ms)d>" % self.__dict__
