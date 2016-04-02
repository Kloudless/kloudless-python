import requests

import helpers
from sdk import http, exceptions

def test_unconfigured_request():
    try:
        http.request(requests.get, 'test')
    except exceptions.ConfigurationException:
        pass

