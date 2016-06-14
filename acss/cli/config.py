import json


def defaults():
    settings = {
        'db_filename': './acss.db',
        'server_host': 'localhost',
        'server_port': 8081,
        'udp_bind_port': 10000,
        'udp_remote_port': 10001,
        'udp_remote_host': '127.0.0.1'
    }
    return settings


def merge(json_file):
    settings = defaults()
    settings.update(json.loads(open(json_file).read()))
    return settings
