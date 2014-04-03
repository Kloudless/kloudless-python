import logging

import dateutil.parser
from datetime import datetime

logger = logging.getLogger('kloudless')

def to_datetime(timestamp):
    """
    Converts ISO 8601 timestamp to datetime object.
    """
    if isinstance(timestamp, datetime) or timestamp is None:
        return timestamp
    elif isinstance(timestamp, basestring):
        return dateutil.parser.parse(timestamp)
    else:
        raise Exception("Unable to convert %s to a datetime object." %
                        timestamp)

def to_iso(obj):
    """
    Converts datetime object to an ISO 8601 timestamp.
    """
    if isinstance(obj, basestring) or obj is None:
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
