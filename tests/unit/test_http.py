import requests

import helpers
from kloudless import http, exceptions

def test_unconfigured_request():
    try:
        http.request(requests.get, 'test')
    except exceptions.ConfigurationException:
        pass

