import sqlite3
import sys
import json

from waitress import serve

from pyramid.config import Configurator
from pyramid.response import Response

from acss.db import DB
from acss.client import Server
from acss.cli import config as config_


def api_tracks(request):
    return request.db().get_tracks()

def api_track_bestlaps(request):
    return request.db().get_best_laps(request.matchdict['track_name'])

def api_track_bestlaps_with_cars(request):
    return request.db().get_best_laps(request.matchdict['track_name'],
        car_names=request.matchdict['car_names'].split(','))

def api_server_info(request):
    s = request.registry.settings
    try:
        return {'success': True,
            'data': Server.get_info(s['server_host'], s['server_port'])}
    except:
        return {'success': False}

def run():
    if len(sys.argv) != 2:
        sys.stderr.write("Usage: %s <config_file>\n" % (sys.argv[0],))
        sys.exit(1)

    settings = config_.merge(sys.argv[1])

    config = Configurator(settings=settings)

    def add_db(request, reify=True):
        return DB(request.registry.settings.get('db_filename'))

    config.add_request_method(add_db, 'db')

    config.add_route('api_tracks', '/api/tracks')
    config.add_route('api_track_bestlaps', '/api/tracks/{track_name}/bestlaps')
    config.add_route('api_track_bestlaps_with_cars', '/api/tracks/{track_name}/{car_names}/bestlaps')
    config.add_route('api_server_info', '/api/server_info')

    config.add_view(api_tracks, route_name='api_tracks', renderer='json')
    config.add_view(api_track_bestlaps, route_name='api_track_bestlaps',
        renderer='json')
    config.add_view(api_track_bestlaps_with_cars,
        route_name='api_track_bestlaps_with_cars', renderer='json')
    config.add_view(api_server_info, route_name='api_server_info',
        renderer='json')
    config.add_static_view(name='/', path='../web_files/')

    app = config.make_wsgi_app()
    serve(app, host='0.0.0.0', port=settings.get('listen_http_port'))
