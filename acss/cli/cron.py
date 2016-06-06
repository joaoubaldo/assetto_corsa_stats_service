import os
import sys
import re
import logging
import json

from acss.db import DB

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger('acss')

def load_results_from_directory(in_dir, out_db):
    db = DB(out_db)
    in_files = os.listdir(in_dir)

    for filename in in_files:
        file_regex = "^(\d\d\d\d)_(\d\d*)_(\d\d*)_(\d\d*)_(\d\d*)_(.*)\.json$"
        file_match = re.match(file_regex, filename)

        if file_match is None:
            continue

        log.info("Picking file %s" % (filename,))

        year, month, day, hour, minute, type_ = file_match.groups()

        f = open(os.path.join(in_dir, filename), 'r')
        data = json.loads(f.read())
        f.close()

        for driver in data['Result']:
            driver_row = db.get_best_lap(
                driver['DriverGuid'], data['TrackName'], driver['CarModel'])

            def insert_driver():
                db.insert_best_lap(
                    driver['DriverGuid'], driver['DriverName'],
                    data['TrackName'], driver['CarModel'],
                    driver['BallastKG'], driver['BestLap'])

            def delete_driver():
                db.delete_best_lap(
                    driver['DriverGuid'], data['TrackName'], driver['CarModel'])

            if driver['BestLap'] >= 999999:
                continue

            if not driver_row:
                log.info("New id for driver %s" % (driver['DriverName'],))
                insert_driver()
            else:
                if driver['BestLap'] < driver_row['best_lap']:
                    log.info("Driver %s has a bestlap new [%s] old [%s]" % (
                        driver_row['driver_name'], driver, driver_row))
                    delete_driver()
                    insert_driver()


def run():
    if len(sys.argv) != 3:
        sys.stderr.write("Usage: %s <input folder> <sqlite file>" % (
            sys.argv[0],))
        sys.exit(1)

    load_results_from_directory(sys.argv[1], sys.argv[2])
    sys.exit(0)
