import logging

import dateutil.parser
from datetime import datetime

import six

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def to_datetime(timestamp):
    """
    Converts ISO 8601 timestamp to datetime object.
    """
    if isinstance(timestamp, datetime) or timestamp is None:
        return timestamp

    return dateutil.parser.parse(timestamp)

def to_iso(obj):
    """
    Converts datetime object to an ISO 8601 timestamp.
    """
    if isinstance(obj, six.string_types) or obj is None:
        return obj
    elif isinstance(obj, datetime):
        timestamp = obj.isoformat()
        if ('+' not in timestamp and len(timestamp) == 19 and
            not timestamp.endswith('Z')):
            timestamp += 'Z' # UTC
        return timestamp
    else:
        raise Exception("Unable to convert %s to an ISO 8601 timestampe." %
                        obj)
