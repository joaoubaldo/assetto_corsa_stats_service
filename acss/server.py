import urllib2
import json

class Client(object):
    def __init__(self):
        pass

    @classmethod
    def get_entry(cls, host, port=8081, timeout=3.0):
        """
        Returns HTML data containing drivers on the servers, their guid, cars.
        """
        return urllib2.urlopen("http://%s:%d/ENTRY" % (host, port),
            timeout=timeout).read()

    @classmethod
    def get_info(cls, host, port=8081, timeout=3.0):
        """
        Fetchs and returns a json object containing server information.
        """
        return json.loads(urllib2.urlopen("http://%s:%d/INFO" % (host, port),
            timeout=timeout).read())
