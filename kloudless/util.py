import dateutil.parser

def to_datetime(timestamp):
    """
    Converts ISO 8601 timestamp to datetime object.
    """
    if isinstance(timestamp, datetime) or timestamp is None:
        return timestamp
    elif isinstance(timestamp, basestring):
        return dateutil.parser.parse(timestamp)
    else:
        raise Exception("Unable to convert %s to datetime object." % timestamp)
