from collections import namedtuple
import logging

from acudpclient.client import ACUDPClient

from acss.db import DB

log = logging.getLogger('acss_udp')

def ms_to_mmssmmm(ms):
    seconds = ms/1000.0
    mmm = int((seconds - int(seconds))*1000)
    m, s = divmod(seconds, 60)
    return "%02d:%02d.%03d" % (m, s, mmm)


def update_best_lap_callback(self, original_event, car_info):
    lap_row = self.db.get_best_lap(
        car_info['driver_guid'], self.session.track_name,
        car_info['car_model'])
    log.info("Checking if %(driver_name)s has lap to update" % \
        car_info)

    # Update best lap in DB
    lap = original_event
    best_lap = None
    if lap_row:
        if lap['lap_time'] < lap_row['best_lap']:
            best_lap = lap['lap_time']
    else:
        best_lap = lap['lap_time']

    if best_lap:
        self.db.delete_best_lap(car_info['driver_guid'],
            self.session.track_name, car_info['car_model'])
        self.db.insert_best_lap(car_info['driver_guid'],
            car_info['driver_name'],
            self.session.track_name, car_info['car_model'], 0.0,
            best_lap)
        message = "%s new PB %s " % (car_info['driver_name'],
            ms_to_mmssmmm(lap['lap_time']))
        log.info(message)
        self.client.broadcast_message(message)

def welcome_callback(self, source_event, car_info):
    lap_row = self.db.get_best_lap(
        car_info['driver_guid'], self.session.track_name,
        car_info['car_model'])

    if lap_row:
        self.client.broadcast_message("Welcome %s! Best lap is %s " % (
            lap_row['driver_name'],
            ms_to_mmssmmm(lap_row['best_lap'])
        ))


class ACUDPDaemon(object):
    def __init__(self, settings):
        self.session = None
        self.cars = {}
        self.client = ACUDPClient(
            port=settings['udp_bind_port'],
            remote_port=settings['udp_remote_port'])
        self.client.listen()
        self.client.subscribe(self)
        self.db = DB(settings['db_filename'])
        self.car_callbacks = {}

    def update(self):
        return self.client.get_next_event()

    def car_by_id(self, id_):
        for car in self.cars.itervalues():
            if car['car_id'] == id_:
                return car

    def get_car_info(self, car_id, cb=None, source_event=None):
        self.client.get_car_info(car_id)
        if cb:
            if car_id not in self.car_callbacks.keys():
                self.car_callbacks[car_id] = (cb, source_event)
            else:
                log.error("Trying to add a callback for existent car_id %d" % (
                    car_id,))

    def on_ACSP_LAP_COMPLETED(self, event):
        if event['cuts'] == 0:
            self.get_car_info(event['car_id'], update_best_lap_callback, event)

    def on_ACSP_CAR_UPDATE(self, event):
        pass  # self.client.get_car_info(event['car_id'])

    def on_ACSP_CAR_INFO(self, event):
        # Update cars in memory
        self.cars[event['driver_guid']] = event

        # Callbacks for callers that expect updated car info
        if event['car_id'] in self.car_callbacks:
            cb, original_event = self.car_callbacks[event['car_id']]
            cb(self, original_event, event)
            del self.car_callbacks[event['car_id']]

    def on_ACSP_SESSION_INFO(self, event):
        self.session = namedtuple('Session', event.keys())(**event)

    def on_ACSP_NEW_SESSION(self, event):
        self.on_ACSP_SESSION_INFO(event)

    def on_ACSP_CLIENT_EVENT(self, event):
        pass
        # if event['other_car_id'] != 255:
        #     car = self.car_by_id(event['car_id'])
        #     def send_message(self, client_event, car_info):
        #         message = "Car contact! Warning %(driver_name)s " % car_info
        #         log.info(message)
        #         log.info(event)
        #         self.client.broadcast_message(message)
        #
        #     self.client.get_car_info(event['car_id'])
        #     self.car_callbacks[event['car_id']] = (send_message, event)


    def on_ACSP_NEW_CONNECTION(self, event):
        self.cars[event['driver_guid']] = event

    def on_ACSP_CONNECTION_CLOSED(self, event):
        if event['driver_guid'] in self.cars.keys():
            del self.cars[event['driver_guid']]

    def on_ACSP_CLIENT_LOADED(self, event):
        self.get_car_info(event['car_id'], welcome_callback, event)

    def __repr__(self):
        d = self.__dict__
        d.update({'total_cars': len(self.cars),})
        return "<ACSession track=\"%(track)s\" session=\"%(name)s\" "\
            "server_name=\"%(server_name)s\" cars=%(total_cars)d time=%(time)d"\
            " laps=%(laps)d elapsed_ms=%(elapsed_ms)d>" % self.__dict__
