import hashlib
import sqlite3
import time
import logging

log = logging.getLogger('acss')

def _dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def best_lap_id(track, driver, car):
    return hashlib.sha224("%s-%s-%s" % (driver, track,
        car)).hexdigest()

class DB(object):
    def __init__(self, db_filename):
        self.db_filename = db_filename
        self.dbc = self.get_sqlite_dbconnection()
        self.prepare_db()

    def get_sqlite_dbconnection(self):
        dbc = sqlite3.connect(self.db_filename)
        dbc.row_factory = _dict_factory
        return dbc

    def prepare_db(self):
        c = self.dbc.cursor()

        try:
            c.execute('''CREATE TABLE best_laps
                         (id text,
                        driver_guid text,
                        driver_name text,
                        track_name text,
                        car_name text,
                        ballast_kg int,
                        last_update text,
                        best_lap bigint)''')
        except sqlite3.OperationalError:
            log.info('Table best_laps already created')

    def get_tracks(self):
        c = self.dbc.cursor()
        query = """select distinct track_name
            from best_laps
            order by last_update desc"""
        c.execute(query)
        return [t['track_name'] for t in c.fetchall()]

    def get_best_laps(self, track_name, limit=None, car_names=None):
        query = """select driver_name, track_name, best_lap, car_name
                    from best_laps
                    where """
        where = [ ('track_name', track_name), ('car_name', car_names) ]
        fields, values = [], []
        infields, invalues = [], []

        for field, value in where:
            if value is None:
                continue
            if isinstance(value, list):
                infields.append(field)
                invalues.append(value)
            else:
                fields.append(field)
                values.append(value)
        query += ' and '.join(["%s = ?" % (f,) for f in fields])

        for idx, field in enumerate(infields):
            vals = invalues[idx]
            query += " and %s in (%s)" % (field, ', '.join('?'*len(vals)))
            values.extend(vals)

        if limit is not None:
            query += " limit %d" % (limit,)
        print query, values
        c = self.dbc.cursor()
        c.execute(query, values)
        data = c.fetchall()

        c.execute(
            """select last_update
            from best_laps
            order by last_update desc limit 1""")
        last_update = c.fetchone()
        if last_update:
            last_update = last_update['last_update']

        return {'data': data,
            'last_update': last_update}

    def get_best_lap_by_id(self, id_):
        c = self.dbc.cursor()
        c.execute(
            "select * from best_laps where id = ?", (id_,))
        return c.fetchone()

    def get_best_lap(self, driver_guid, track, car):
        id_ = best_lap_id(track, driver_guid, car)
        c = self.dbc.cursor()
        c.execute(
            "select * from best_laps where id = ?", (id_,))
        return c.fetchone()

    def insert_best_lap(self, driver_guid, driver, track, car, ballast, best_lap):
        id_ = best_lap_id(track, driver_guid, car)
        c = self.dbc.cursor()
        c.execute("""insert into best_laps(id, driver_guid,
                driver_name, track_name, car_name, ballast_kg,
                best_lap, last_update)
            values (?,?,?,?,?,?,?,?)""",
            (id_, driver_guid, driver, track, car, ballast, best_lap,
                time.time()))
        self.dbc.commit()

    def delete_best_lap(self, driver_guid, track, car):
        id_ = best_lap_id(track, driver_guid, car)
        c = self.dbc.cursor()
        c.execute("""delete from best_laps where id = ?""",
            (id_,))
        self.dbc.commit()
