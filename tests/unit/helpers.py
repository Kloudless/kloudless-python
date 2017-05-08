import sys
import imp

import kloudless

from functools import wraps


test_configuration = {"api_key" : "FAKE"}

def configured_test(f):
    """
    This configures and unconfigures the kloudless client for test requests
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        default_config = kloudless.config.configure()
        kloudless.configure(**test_configuration)
        result = f(*args, **kwargs)
        kloudless.configure(**default_config)
        return result
    return wrapper



account_list = '{"total": 7, "count": 7, "page": 1, "objects": [{"id": 15, "account": "test test", "active": true, "service": "bitcasa", "created": "2014-04-04T22:13:53.524670Z", "modified": "2014-04-04T22:13:53.524778Z"}, {"id": 8, "account": "test@example.com", "active": true, "service": "box", "created": "2014-04-02T21:06:40.051854Z", "modified": "2014-04-09T06:47:25.418883Z"}, {"id": 9, "account": "test@example.com", "active": true, "service": "box", "created": "2014-04-02T21:11:29.302179Z", "modified": "2014-04-05T04:52:58.101067Z"}, {"id": 25, "account": "test@example.com", "active": true, "service": "copy", "created": "2014-04-18T16:01:43.131735Z", "modified": "2014-04-18T16:02:37.140884Z"}, {"id": 6, "account": "test@example.com", "active": true, "service": "dropbox", "created": "2014-03-30T02:39:36.145255Z", "modified": "2014-04-01T20:38:55.691493Z"}, {"id": 16, "account": "test@example.com", "active": true, "service": "gdrive", "created": "2014-04-04T22:28:11.181818Z", "modified": "2014-04-04T22:28:11.181884Z"}, {"id": 7, "account": "test@example.com", "active": true, "service": "gdrive", "created": "2014-04-01T20:48:23.472545Z", "modified": "2014-04-04T05:17:21.060602Z"}]}'

account = '{"id": 7, "account": "test@example.com", "active": true, "service": "gdrive", "created": "2014-04-01T20:48:23.472545Z", "modified": "2014-04-23T21:34:49.427199Z"}'

root_folder_contents = '{"count": 18, "objects": [{"account": "7", "name": "dogedog.png", "created": "2014-04-01T00:54:02.177000Z", "modified": "2014-04-01T23:36:54.122000Z", "type": "file", "id": "fMEI3NFBzcEhad3BzTVZFeFFTbGd0U3paUU9FVQ==", "size": "4420"}, {"account": "7", "name": "dogedog.png", "created": "2014-04-01T00:55:31.487000Z", "modified": "2014-04-01T00:55:32.949000Z", "type": "file", "id": "fMEI3NFBzcEhad3BzTWVXNWFTRk5RUVVkRU1GRQ==", "size": "4420"}, {"account": "7", "name": "derp.data", "created": "2014-03-28T20:26:56.630000Z", "modified": "2014-03-28T20:26:56.285000Z", "type": "file", "id": "fMEI3NFBzcEhad3BzTVlubHlUVUU1UTJoWVYyYw==", "size": "0"}, {"account": "7", "name": "Kloudless", "created": "2013-04-28T01:08:44.983000Z", "modified": "2014-02-25T20:05:24.707000Z", "type": "folder", "id": "fMEI3NFBzcEhad3BzTVNHWlpZbmhMYjI4NU9Vaw==", "size": "0"}, {"account": "7", "name": "Automation", "created": "2013-04-28T01:08:50.832000Z", "modified": "2014-02-25T20:05:26.491000Z", "type": "folder", "id": "fMEI3NFBzcEhad3BzTVVEUk1YMFJZWTFSNGJraw==", "size": "0"}, {"account": "7", "name": "Test Document 2", "created": "2013-12-31T20:17:09.938000Z", "modified": "2013-12-31T20:17:25.780000Z", "type": "file", "id": "fMTlZR05HZ3VKV3VKcnR1SGgwaXdWSlMzaG5QaE1xaEczTEpJempQZjd6RFE=", "size": "0"}, {"account": "7", "name": "meowow", "created": "2013-12-31T03:04:33.052000Z", "modified": "2013-12-31T03:04:36.310000Z", "type": "file", "id": "fMURYRjhLc1p2WDhrbTNQZkNWRDhyNVNsYjhxYVR3MFc2ZlcyamN4QUJhQ1U=", "size": "0"}, {"account": "7", "name": "bluh", "created": "2013-12-30T23:19:47.214000Z", "modified": "2013-12-31T02:15:38.162000Z", "type": "file", "id": "fMXJXUlEzOEpjM3ZSSXhXVzh4bHpud3VaUTlrVFptaUJhV1ktLWFtdzhIUXM=", "size": "0"}, {"account": "7", "name": "foo.html", "created": "2013-12-31T01:58:45.454000Z", "modified": "2013-12-31T01:58:45.454000Z", "type": "file", "id": "fMEI3NFBzcEhad3BzTWNteFlXRE5JWVZoQmRXTQ==", "size": "104"}, {"account": "7", "name": "\u2600 \u2601 \u2602 \u2603 \u2604 \u2605 \u2606 \u2607 \u2608 \u2609 \u260a \u260b", "created": "2013-12-31T00:19:33.415000Z", "modified": "2013-12-31T00:19:33.415000Z", "type": "file", "id": "fMEI3NFBzcEhad3BzTU5rZEVkMDkxTjFvME5Gaw==", "size": "2219663"}, {"account": "7", "name": "Securing_Your_Mac-A_Guide_To_Hardening_Your_Browser.pdf", "created": "2013-12-30T23:44:22.077000Z", "modified": "2013-12-30T23:44:22.077000Z", "type": "file", "id": "fMEI3NFBzcEhad3BzTWJHbEtiakJYYTFwb05EUQ==", "size": "873171"}, {"account": "7", "name": "TEST_SPREADSHEET", "created": "2013-12-30T23:17:06.085000Z", "modified": "2013-12-30T23:17:38.665000Z", "type": "file", "id": "fMEFyNFBzcEhad3BzTWRIVlFjbFkwU0dGcVdraFlkMmhhU1dZM1IwOUxkSGM=", "size": "0"}, {"account": "7", "name": "TEST", "created": "2013-12-30T21:38:37.171000Z", "modified": "2013-12-30T21:38:40.646000Z", "type": "file", "id": "fMUVHTk1GaHVtcUVPRE0xNHVpYTBpdDFPcG5sNEVVSFBRQWRFTmN0NmpFUUU=", "size": "0"}, {"account": "7", "name": "derp.burp", "created": "2013-11-27T01:23:10.659000Z", "modified": "2013-11-27T01:23:10.659000Z", "type": "file", "id": "fMEI3NFBzcEhad3BzTVZqQXdRMkpIVVdkNGJtOA==", "size": "1024000"}, {"account": "7", "name": "derp.fffuuu", "created": "2013-11-27T00:57:45.533000Z", "modified": "2013-11-27T00:57:45.533000Z", "type": "file", "id": "fMEI3NFBzcEhad3BzTWEyMUNXWHA2YWxWMlVGVQ==", "size": "10240000"}, {"account": "7", "name": "Kloudless Sent Files", "created": "2013-11-20T21:37:18.445000Z", "modified": "2013-11-20T21:37:18.445000Z", "type": "folder", "id": "fMEI3NFBzcEhad3BzTVZtMHdXbmRFZFhoS2FVaw==", "size": "0"}, {"account": "7", "name": "gangam_style.jpg", "created": "2013-06-27T21:11:29.022000Z", "modified": "2013-06-27T21:11:29.022000Z", "type": "file", "id": "fMEI3NFBzcEhad3BzTWJYQllSWEptUjJkV2JHcw==", "size": "160816"}, {"account": "7", "name": "Argentina.png", "created": "2013-06-11T07:59:41.038000Z", "modified": "2013-06-11T07:59:41.038000Z", "type": "file", "id": "fMEI3NFBzcEhad3BzTWNFMTVjWEJqTUVJNU4xVQ==", "size": "42260"}]}'

folder_data = '{"account": "7", "name": "Kloudless", "created": "2013-04-28T01:08:44.983000Z", "modified": "2014-02-25T20:05:24.707000Z", "type": "folder", "id": "fMEI3NFBzcEhad3BzTVNHWlpZbmhMYjI4NU9Vaw==", "size": "0"}'

file_data =  '{"account": "7", "name": "derp.burp", "created": "2013-11-27T01:23:10.659000Z", "modified": "2013-11-27T01:23:10.659000Z", "type": "file", "id": "fMEI3NFBzcEhad3BzTVZqQXdRMkpIVVdkNGJtOA==", "size": "1024000"}'

file_contents = "Woooo this is a test file!"

property_data = '{"properties": [{"key": "department", "value": "engineering", "created": "2015-03-17T20:42:18.627533Z", "modified": "2015-03-17T20:42:18.627533Z"}, { "key": "readonly", "value": "true", "created": "2015-03-17T20:42:18.627533Z", "modified": "2015-03-17T20:42:18.627533Z"}]}'
