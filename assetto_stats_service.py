import sqlite3

from waitress import serve

from pyramid.config import Configurator
from pyramid.response import Response

__VERSION__ = 0.1

def get_sqlite_dbconnection(filename):
    dbc = sqlite3.connect(filename)

    def dict_factory(cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    dbc.row_factory = dict_factory
    return dbc

def api_tracks(request):
    dbc = get_sqlite_dbconnection("out.db")
    c = dbc.cursor()
    c.execute(
        "select distinct track_name from drivers_lap order by last_update desc")
    return [t['track_name'] for t in c.fetchall()]

def api_track_bestlaps(request):
    track_name = request.matchdict['track_name']
    dbc = get_sqlite_dbconnection("out.db")
    c = dbc.cursor()
    c.execute(
        """select driver_name, track_name, best_lap, car_name from drivers_lap
        where track_name = ? order by car_name asc, best_lap desc""",
        (track_name,))
    return c.fetchall()

if __name__ == '__main__':
    config = Configurator()

    config.add_route('api_tracks', '/api/tracks')
    config.add_route('api_track_bestlaps', '/api/tracks/{track_name}/bestlaps')

    config.add_view(api_tracks, route_name='api_tracks', renderer='json')
    config.add_view(api_track_bestlaps, route_name='api_track_bestlaps',
        renderer='json')

    app = config.make_wsgi_app()
    serve(app, host='0.0.0.0', port=8001)
