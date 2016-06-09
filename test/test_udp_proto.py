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


f = open('ac_out', 'r')

def readByte():
    return struct.unpack('B', f.read(1))[0]

def readSingle():
    return struct.unpack('<f', f.read(4))[0]

def readVector3f():
    return {'x':readSingle(), 'y':readSingle(), 'z':readSingle()}

def readString32():
    length = readByte()
    return f.read(length*4).decode('utf32')

def readString8():
    length = readByte()
    return f.read(length).decode('ascii')

def readUInt16():
    return struct.unpack('<H', f.read(2))[0]

def readUInt32():
    return struct.unpack('<L', f.read(4))[0]

def readInt32():
    return struct.unpack('<l', f.read(4))[0]

def run():
    while 1:
        type_ = readByte()
        if type_ == act['ACSP_VERSION']:
            readByte()  # proto version
        elif type_ == act['ACSP_CAR_UPDATE']:
            print "ACSP_CAR_UPDATE"
            print readByte()  # car id
            print readVector3f()  # pos
            print readVector3f()  # vel
            print readByte()  # gear
            print readUInt16()  # engine
            print readSingle()  # normalized_spline_pos
        elif type_ == act['ACSP_CLIENT_EVENT']:
            print "ACSP_CLIENT_EVENT"
            ev_type = readByte()  # ev_type
            print readByte()  # car id
            other_car_id = 255
            if ev_type == act['ACSP_CE_COLLISION_WITH_CAR']:
                other_car_id = readByte()
            elif ev_type == act['ACSP_CE_COLLISION_WITH_ENV']:
                pass

            print readSingle()  # impact speed
            print readVector3f()  # world_pos
            print readVector3f()  # rel_pos
        elif type_ == act['ACSP_CAR_INFO']:
            print "ACSP_CAR_INFO"
            print readByte()  # car id
            print readByte() != 0  # is connected
            print readString32()  # model
            print readString32()  # skin
            print readString32()  # drivername
            print readString32()  # driver_team
            print readString32()  # driver_guid
        elif type_ == act['ACSP_CHAT']:
            print "ACSP_CHAT"
            print readByte()  # car id
            print readString32()  # msg
        elif type_ == act['ACSP_LAP_COMPLETED']:
            print "ACSP_LAP_COMPLETED"
            print readByte()  # car id
            print readUInt32()  # laptime
            print readByte()  # cuts
            cars_count = readByte()  # cars_count
            for i in range(cars_count):
                print readByte()  # rcar_id
                print readUInt32()  # rtime
                print readUInt16()  # rlaps
            print readSingle()  # grip_level
        elif type_ == act['ACSP_END_SESSION']:
            print "ACSP_END_SESSION"
            print readString32()  # filename json
        elif type_ == act['ACSP_CLIENT_LOADED']:
            print "ACSP_CLIENT_LOADED"
            print readByte()  # car id
        elif type_ == act['ACSP_CONNECTION_CLOSED']:
            print "ACSP_CONNECTION_CLOSED"
            print readString32()  # driver name
            print readString32()  # driver guid
            print readByte()  # car id
            print readString8()  # car model
            print readString8()  # car skin
        elif type_ == act['ACSP_ERROR']:
            print "ACSP_ERROR"
            print readString32()  # error
        elif type_ == act['ACSP_NEW_CONNECTION']:
            print "ACSP_NEW_CONNECTION"
            print readString32()  # driver name
            print readString32()  # driver guid
            print readByte()  # car id
            print readString8()  # car model
            print readString8()  # car skin
        elif type_ == act['ACSP_NEW_SESSION'] or type_ == act['ACSP_SESSION_INFO']:
            print "New session started"

            print "Session Info"  # ACSP_SESSION_INFO
            version = readByte()  # UDP Plugin protocol version, in case you miss the first ACSP_VERSION message sent by the server at startup
            sess_index = readByte()  # The index of the session in the message
            current_session_index = readByte()  #; // The index of the current session in the server
            session_count = readByte()  #; // The number of sessions in the server
            print version, sess_index, current_session_index, session_count

            print readString32()  # server_name
            print readString8()  # track_name
            print readString8()  # track_config
            print readString8()  # session name
            print readByte()  # type
            print readUInt16()  # time
            print readUInt16()  # laps
            print readUInt16()  # wait time
            print readByte()  # amb temp
            print readByte()  # road temp
            print readString8()  # weather graphs
            print readInt32()  # elapsedMS

run()
