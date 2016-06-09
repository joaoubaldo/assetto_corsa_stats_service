import struct

raw_proto = """public const byte ACSP_NEW_SESSION = 50;
public const byte ACSP_NEW_CONNECTION = 51;
public const byte ACSP_CONNECTION_CLOSED = 52;
public const byte ACSP_CAR_UPDATE = 53;
public const byte ACSP_CAR_INFO = 54; // Sent as response to ACSP_GET_CAR_INFO command
public const byte ACSP_END_SESSION = 55;
public const byte ACSP_LAP_COMPLETED = 73;
public const byte ACSP_VERSION = 56;
public const byte ACSP_CHAT = 57;
public const byte ACSP_CLIENT_LOADED = 58;
public const byte ACSP_SESSION_INFO = 59;
public const byte ACSP_ERROR = 60;

// EVENTS
public const byte ACSP_CLIENT_EVENT = 130;

// EVENT TYPES
public const byte ACSP_CE_COLLISION_WITH_CAR = 10;
public const byte ACSP_CE_COLLISION_WITH_ENV = 11;

// COMMANDS
public const byte ACSP_REALTIMEPOS_INTERVAL = 200;
public const byte ACSP_GET_CAR_INFO = 201;
public const byte ACSP_SEND_CHAT = 202; // Sends chat to one car
public const byte ACSP_BROADCAST_CHAT = 203; // Sends chat to everybody
public const byte ACSP_GET_SESSION_INFO = 204;
public const byte ACSP_SET_SESSION_INFO = 205;
public const byte ACSP_KICK_USER = 206;
public const byte ACSP_NEXT_SESSION = 207;
public const byte ACSP_RESTART_SESSION = 208;
public const byte ACSP_ADMIN_COMMAND = 209; // Send message plus a stringW with the command
"""

act = {}

for line in raw_proto.splitlines():
    start = line.find("ACSP")
    if start >= 0:
        line = line[start:]
        name, val = line.split("=")
        val = val[:val.find(';')]
        act[name.strip()] = int(val.strip())


def readByte(f):
    return struct.unpack('B', f.read(1))[0]

def readSingle(f):
    return struct.unpack('<f', f.read(4))[0]

def readVector3f(f):
    return {'x':readSingle(f), 'y':readSingle(f), 'z':readSingle(f)}

def readString32(f):
    length = readByte(f)
    return f.read(length*4).decode('utf32')

def readString8(f):
    length = readByte(f)
    return f.read(length).decode('ascii')

def readUInt16(f):
    return struct.unpack('<H', f.read(2))[0]

def readUInt32(f):
    return struct.unpack('<L', f.read(4))[0]

def readInt32(f):
    return struct.unpack('<l', f.read(4))[0]

class ACUDPProto(object):

    @classmethod
    def process_event(cls, file_obj):
        try:
            type_ = readByte(file_obj)
        except struct.error:
            return None

        event = {'type': type_}
        if type_ == act['ACSP_VERSION']:
            event.update({'proto_version': readByte(file_obj)})
        elif type_ == act['ACSP_CAR_UPDATE']:
            event.update({
                'car_id': readByte(file_obj),
                'pos': readVector3f(file_obj),
                'vel': readVector3f(file_obj),
                'gear': readByte(file_obj),
                'engine_rpm': readUInt16(file_obj),
                'normalized_spline_pos': readSingle(file_obj)
            })
        elif type_ == act['ACSP_CLIENT_EVENT']:
            ev_type = readByte(file_obj)  # ev_type
            car_id = readByte(file_obj)  # car id
            other_car_id = 255
            if ev_type == act['ACSP_CE_COLLISION_WITH_CAR']:
                other_car_id = readByte(file_obj)
            elif ev_type == act['ACSP_CE_COLLISION_WITH_ENV']:
                pass
            event.update({
                'ev_type': ev_type,
                'car_id': car_id,
                'other_car_id': other_car_id,
                'impact_speed': readSingle(file_obj),
                'world_pos': readVector3f(file_obj),
                'rel_pos': readVector3f(file_obj)
            })

        elif type_ == act['ACSP_CAR_INFO']:
            event.update({
                'car_id': readByte(file_obj),
                'is_connected': readByte(file_obj) != 0,
                'car_model': readString32(file_obj),
                'car_skin': readString32(file_obj),
                'driver_name': readString32(file_obj),
                'driver_team': readString32(file_obj),
                'driver_guid': readString32(file_obj)
            })
        elif type_ == act['ACSP_CHAT']:
            event.update({
                'car_id': readByte(file_obj),
                'message': readString32(file_obj)
            })
        elif type_ == act['ACSP_LAP_COMPLETED']:
            event.update({
                'car_id': readByte(file_obj),
                'lap_time': readUInt32(file_obj),
                'cuts': readByte(file_obj),
                'cars': []
            })
            cars_count = readByte(file_obj)
            for i in range(cars_count):
                event['cars'].append({
                    'rcar_id': readByte(file_obj),
                    'rtime': readUInt32(file_obj),
                    'rlaps': readUInt16(file_obj)
                })
            event['grip_level'] = readSingle(file_obj)
        elif type_ == act['ACSP_END_SESSION']:
            event.update({'filename': readString32(file_obj)})
        elif type_ == act['ACSP_CLIENT_LOADED']:
            event.update({'car_id': readByte(file_obj)})
        elif type_ == act['ACSP_CONNECTION_CLOSED']:
            event.update({
                'driver_name': readString32(file_obj),
                'driver_guid': readString32(file_obj),
                'car_id': readByte(file_obj),
                'car_model': readString8(file_obj),
                'car_skin': readString8(file_obj)
            })
        elif type_ == act['ACSP_ERROR']:
            event.update({'message': readString32(file_obj)})
        elif type_ == act['ACSP_NEW_CONNECTION']:
            event.update({
                'driver_name': readString32(file_obj),
                'driver_guid': readString32(file_obj),
                'car_id': readByte(file_obj),
                'car_model': readString8(file_obj),
                'car_skin': readString8(file_obj)
            })
        elif type_ == act['ACSP_NEW_SESSION'] or type_ == act['ACSP_SESSION_INFO']:
            event.update({
                'proto_version': readByte(file_obj),
                'session_index': readByte(file_obj),
                'current_sess_index': readByte(file_obj),
                'session_count': readByte(file_obj),
                'server_name': readString32(file_obj),
                'track_name': readString8(file_obj),
                'track_config': readString8(file_obj),
                'name': readString8(file_obj),
                'type': readByte(file_obj),
                'time': readUInt16(file_obj),
                'laps': readUInt16(file_obj),
                'wait_time': readUInt16(file_obj),
                'ambient_temp': readByte(file_obj),
                'track_temp': readByte(file_obj),
                'weather_graph': readString8(file_obj),
                'elapsed_ms': readInt32(file_obj)
            })
        return event


def run():

    f = open('ac_out', 'r')
    while 1:
        event = ACUDPProto.process_event(f)
        if event :
            print event
        sleep(.2)

run()
