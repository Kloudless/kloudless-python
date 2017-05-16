from .util import logger
from . import config
from . import exceptions

import functools
import json
import time
import six

from abc import ABCMeta, abstractproperty
from requests.structures import CaseInsensitiveDict


class BaseAuth:
    __metaclass__ = ABCMeta

    scheme = abstractproperty()

    def __init__(self, key):
        self.key = key

    @property
    def auth_header(self):
        return '%s %s' % (self.scheme, self.key)

    def __call__(self, request):
        request.headers['Authorization'] = self.auth_header
        return request

class APIKeyAuth(BaseAuth):
    scheme = 'APIKey'

class DevKeyAuth(BaseAuth):
    scheme = 'DeveloperKey'

class BearerTokenAuth(BaseAuth):
    scheme = 'Bearer'

_get_requestor = functools.partial

def request(method, path, configuration=None, **kwargs):
    if configuration is None: configuration = {}
    configuration = config.merge(configuration)

    if path.startswith('applications'):
        if not configuration['dev_key']:
            raise exceptions.ConfigurationException(
                "A Developer Key must be provided. You can get one at "
                "https://developers.kloudless.com and set it by calling "
                "'kloudless.configure(dev_key=\"DEV_KEY\")' prior to making "
                "requests.")

        kwargs['auth'] = DevKeyAuth(configuration['dev_key'])

    elif configuration['api_key']:
        kwargs['auth'] = APIKeyAuth(configuration['api_key'])
    elif configuration['token']:
        kwargs['auth'] = BearerTokenAuth(configuration['token'])
    else:
        raise exceptions.ConfigurationException(
            "An API Key or Bearer Token must be provided. You can get an API Key at "
            "https://developers.kloudless.com and set it by calling "
            "'kloudless.configure(api_key=\"API_KEY\")' prior to making "
            "requests. You can get a Bearer token by authenticating an account and "
            "set it by calling 'kloudless.configure(token=\"TOKEN\")' as well.")

    url = "%s/v%s/%s" % (configuration['base_url'],
                         configuration['api_version'],
                         path)

    headers = kwargs['headers'] = CaseInsensitiveDict(kwargs.get('headers') or {})

    # Set default headers if not present
    for header_key, header_val in six.iteritems(configuration.get('headers') or {}):
        if header_val is not None and header_key not in headers:
            headers[header_key] = header_val

    # Set content type
    if kwargs.get('data'):
        ctype = headers.setdefault('Content-Type', 'application/json')
        if ctype.lower() == 'application/json':
            kwargs['data'] = json.dumps(kwargs['data'])

    # Make request
    requestor = _get_requestor(method, url, **kwargs)
    response = _request(requestor, configuration)
    return response

def _request(requestor, configuration):
    response = requestor()

    if not response.ok:
        logger.error("Request to '%s' failed: %s - %s" %
                     (response.url, response.status_code, response.text))
        if response.status_code == 403:
            raise exceptions.AuthenticationException(response=response)
        elif response.status_code == 401:
            raise exceptions.AuthorizationException(response=response)
        elif response.status_code == 429:
            throttle_obj = configuration.get('throttle_retry_strategy')
            if not throttle_obj:
                raise exceptions.RateLimitException(response=response)

            delay = throttle_obj.track_and_delay(response)
            if delay is not None:
                time.sleep(delay)
                return _request(requestor, configuration)
        elif response.status_code >= 500:
            raise exceptions.ServerException(response=response)
        else:
            raise exceptions.APIException(response=response)
    else:
        logger.debug("Request to '%s' succeeded. Status code: %s" %
                     (response.url, response.status_code))

    return response
