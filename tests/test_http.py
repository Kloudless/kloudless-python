from py.test import raises
import mock
import requests

from kloudless import http
from kloudless.exceptions import ConfigurationException

def test_unconfigured_request():
    with raises(ConfigurationException):
        http.request(requests.get, 'test')
