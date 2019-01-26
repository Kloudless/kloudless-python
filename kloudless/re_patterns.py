from __future__ import unicode_literals

import re

events_pattern = re.compile(r"accounts/(?:\d+|me)/"
                            r"(?:events/?$"
                            r"|events/?\?[^/]+$)")

full_account_pattern = re.compile(r'https?://.+?/v\d/accounts/(?:[\d]+|me)')

download_file_patterns = re.compile(r'storage/files/.+?/contents'
                                    r'|storage/files/.+?/thumbnail'
                                    r'|meta/licenses/.+?/contents')

primary_calendar_alias = re.compile('cal/calendars/primary/?$')
