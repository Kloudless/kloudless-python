from . import throttling

import six

_configuration = {
    'api_key': None,
    'dev_key': None,
    'token': None,
    'api_version': '1',
    'base_url': 'https://api.kloudless.com',
    'throttle_retry_strategy': throttling.ExpFallback(),
    'headers': {
        # Set to a value other than None to include the header in each
        # API request.
        'X-Kloudless-Raw-Data': None,
        'X-Kloudless-As-User': None,
        # Include any other headers here you would like to be sent.
    }
}

def configure(**params):
    """Update configuration based on params. Returns new configuration.
    To retrieve existing configuration, call this method with no arguments.

    :param api_key: API Key
    :param api_version: API Version
    :param base_url: Base API URL
    """
    global _configuration
    if not params:
        return _configuration

    _configuration = merge(params)
    return _configuration

def merge(config):
    result = _configuration.copy()
    for k, v in six.iteritems(config):
        if k in result:
            result[k] = v
    return result
