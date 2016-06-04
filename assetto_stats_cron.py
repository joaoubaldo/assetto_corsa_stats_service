import os
import sys
import re
import sqlite3
import logging
import json
import hashlib
import time

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger('ac_parser')

def prepare_db(dbc):
    c = dbc.cursor()

    try:
        c.execute('''CREATE TABLE files
                     (filename text,
                      processed_ts text,
                      processed tinyint)''')
    except sqlite3.OperationalError:
        log.info('Table files already created')

    try:
        c.execute('''CREATE TABLE drivers_lap
                     (id text,
                    driver_guid text,
                    driver_name text,
                    track_name text,
                    car_name text,
                    ballast_kg int,
                    last_update text,
                    best_lap bigint)''')
    except sqlite3.OperationalError:
        log.info('Table drivers_lap already created')

def get_drivers_lap_id(track, driver):
    return hashlib.sha224("%s-%s-%s" % (driver['DriverGuid'], track,
        driver['CarModel'])).hexdigest()

def parse(in_dir, out_db):
    dbc = sqlite3.connect(out_db)

    def dict_factory(cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    dbc.row_factory = dict_factory
    prepare_db(dbc)
    in_files = os.listdir(in_dir)
    c = dbc.cursor()

    for filename in in_files:
        reg_ex = "^(\d\d\d\d)_(\d\d*)_(\d\d*)_(\d\d*)_(\d\d*)_(.*)\.json$"
        file_match = re.match(reg_ex, filename)
        
        if file_match is None:
            continue

        log.info("Picking file %s" % (filename,))

        year, month, day, hour, minute, type_ = file_match.groups()

        f = open(os.path.join(in_dir, filename), 'r')
        data = json.loads(f.read())

        for driver in data['Result']:
            id_ = get_drivers_lap_id(data['TrackName'], driver)

            c.execute(
                "select * from drivers_lap where id = ?", (id_,))
            driver_row = c.fetchone()

            def insert_driver():
                c.execute("""insert into drivers_lap(id, driver_guid,
                        driver_name, track_name, car_name, ballast_kg,
                        best_lap, last_update)
                    values (?,?,?,?,?,?,?,?)""",
                    (id_, driver['DriverGuid'], driver['DriverName'],
                    data['TrackName'], driver['CarModel'],
                    driver['BallastKG'], driver['BestLap'], time.time()))
                dbc.commit()

            def delete_driver():
                c.execute("""delete from drivers_lap where id = ?""",
                    (id_,))
                dbc.commit()

            if driver['BestLap'] >= 999999:
                continue

            if not driver_row:
                log.info("New id for driver %s" % (
                    driver['DriverName'],))
                insert_driver()
            else:
                if driver['BestLap'] < driver_row['best_lap']:
                    log.info("Driver %s has a bestlap new [%s] old [%s]" % (
                        driver_row['driver_name'], driver, driver_row))
                    delete_driver()
                    insert_driver()


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.stderr.write("Usage: %s <input folder> <sqlite file>" % (
            sys.argv[0],))
        sys.exit(1)

    parse(sys.argv[1], sys.argv[2])
    sys.exit(0)
