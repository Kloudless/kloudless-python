from __future__ import unicode_literals

import logging
from datetime import datetime

import six
from dateutil import parser

from .config import configuration

if six.PY2:
    from urlparse import urljoin
elif six.PY3:
    from urllib.parse import urljoin

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def to_datetime(timestamp):
    """
    Converts ISO 8601 timestamp to datetime object.
    """
    if isinstance(timestamp, datetime) or timestamp is None:
        return timestamp

    return parser.parse(timestamp)


def to_iso(obj):
    """
    Converts datetime object to an ISO 8601 timestamp.
    """
    if isinstance(obj, six.string_types) or obj is None:
        return obj
    elif isinstance(obj, datetime):
        timestamp = obj.isoformat()
        if ('+' not in timestamp and len(timestamp) == 19
                and not timestamp.endswith('Z')):
            timestamp += 'Z'  # UTC
        return timestamp
    else:
        raise Exception(
            "Unable to convert {} to an ISO 8601 timestamp.".format(obj)
        )


def get_config(name, overwrite=None):
    if overwrite is not None:
        return overwrite

    return configuration.get(name)


def url_join(prefix, suffix):

    if not suffix:
        return prefix
    # when suffix is complete url endpoint, used in resources.base.Response
    if suffix.startswith(prefix):
        return suffix
    # Always adding trailing slash to prefix to stack path
    return urljoin('{}/'.format(prefix), suffix.lstrip('/'))


def construct_kloudless_endpoint(path='', base_url=None, api_version=None):

    base_url = get_config('base_url', base_url)
    api_version = get_config('api_version', api_version)
    prefix = url_join(base_url, 'v{}'.format(api_version))

    return url_join(prefix, path)
