configuration = {
    'api_key': None,
    'api_version': '0',
    'base_url': 'https://api.kloudless.com'
    }

def configure(**params):
    """Update configuration based on params.

    :param api_key: API Key
    :param api_version: API Version
    :param base_url: Base API URL
    """
    global configuration
    configuration = merge(params)
    return configuration

def merge(config):
    result = configuration.copy()
    for k, v in config.iteritems():
        if k in result:
            result[k] = v
    return result
