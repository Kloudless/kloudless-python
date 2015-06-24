from .util import logger
from . import config
from . import exceptions

import functools
import json

class APIKeyAuth(object):
    def __init__(self, api_key):
        self.api_key = api_key

    def __call__(self, request):
        request.headers['Authorization'] = 'ApiKey %s' % self.api_key
        return request

def request(method, path, configuration=None, **kwargs):
    if configuration is None: configuration = {}
    configuration = config.merge(configuration)

    if not configuration['api_key']:
        raise exceptions.ConfigurationException(
            "An API Key must be provided. You can get one at "
            "https://developers.kloudless.com and set it by calling "
            "'kloudless.configure(api_key=\"API_KEY\")' prior to making "
            "requests.")

    url = "%s/v%s/%s" % (configuration['base_url'],
                         configuration['api_version'],
                         path)
    kwargs['auth'] = APIKeyAuth(configuration['api_key'])

    headers = kwargs.setdefault('headers', {})

    if kwargs.get('data') and not kwargs.get('files'):
        ctype = headers.setdefault('Content-Type', 'application/json')
        if ctype.lower() == 'application/json':
            kwargs['data'] = json.dumps(kwargs['data'])

    requestor = functools.partial(method, url, **kwargs)
    response = _request(requestor)
    return response

def _request(requestor):
    response = requestor()

    if not response.ok:
        logger.error("Request to '%s' failed: %s - %s" %
                     (response.url, response.status_code, response.text))
        if response.status_code == 403:
            raise exceptions.AuthenticationException(response=response)
        elif response.status_code == 401:
            raise exceptions.AuthorizationException(response=response)
        elif response.status_code >= 500:
            raise exceptions.ServerException(response=response)
        else:
            raise exceptions.APIException(response=response)
    else:
        logger.debug("Request to '%s' succeeded. Status code: %s" %
                     (response.url, response.status_code))

    return response
