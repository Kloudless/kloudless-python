from __future__ import unicode_literals

import argparse
import json

from six import iteritems
from six.moves.BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from six.moves.urllib.parse import parse_qs, urlparse

from kloudless import get_authorization_url, get_token_from_code, Account
from kloudless.exceptions import APIException
from kloudless.util import logger

logger.setLevel('DEBUG')

# You should store state in user's session in production instead
state_holder = None


class RequestHandler(BaseHTTPRequestHandler):

    @staticmethod
    def get_query_params(url):
        parse_result = urlparse(url)
        # query_params format: {key1: ['value1'], key2: ['value2']}
        query_params = parse_qs(parse_result.query)
        # clean up the value format to plain string
        params = {k: v[0] for k, v in iteritems(query_params)}
        return params

    def http_redirect(self, url):
        self.send_response(302)
        self.send_header('Location', url)
        self.send_header("Cache-Control", "no-store, must-revalidate")
        self.end_headers()

    def http_json_response(self, status_code, data):
        self.send_response(status_code)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf8'))

    def do_GET(self):

        global state_holder

        redirect_url = 'http://localhost:{}/callback'.format(port)

        if self.path == '/':
            #####################
            #  Server Home Page
            #####################
            html = """
            <html>
                <body>
                    <h1>Welcome to Kloudless Demo Server</h1>
                    <hr>
                    <h2>
                        <a href="/storage">
                            Connect Storage account and retrieve root
                             folder contents in JSON format
                        </a>
                    </h2>
                    <h2>
                        <a href="/calendar">
                            Connect Calendar account and retrieve primary
                             calendar's events in JSON format
                        </a>
                    </h2>
                </body>
            </html>
            """
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(html.encode('utf8'))

        elif self.path == '/storage':
            ##############################
            # To connect Storage service
            ##############################

            url, state = get_authorization_url(app_id,
                                               redirect_uri=redirect_url,
                                               scope='storage')
            state_holder = state  # Store state for security check later

            # Redirect user to start first leg of authorization flow
            self.http_redirect(url)

        elif self.path == '/calendar':
            ###############################
            # To connect Calendar service
            ###############################
            url, state = get_authorization_url(app_id,
                                               redirect_uri=redirect_url,
                                               scope='calendar')
            state_holder = state  # Store state for security check later

            # Redirect user to start first leg of authorization flow
            self.http_redirect(url)

        elif self.path.startswith('/callback'):
            ######################
            #  Callback endpoint
            ######################
            try:
                params = self.get_query_params(self.path)

                # Exchange token from authorization code
                token = get_token_from_code(app_id=app_id, api_key=api_key,
                                            orig_state=state_holder,
                                            orig_redirect_uri=redirect_url,
                                            **params)

                account = Account(token=token)
                # Request to https://api.kloudless.com/account/me
                account_resp = account.get()
                resp_data = {
                    'msg': 'Successfully retrieving JSON data after connecting'
                           ' your account.',
                    'account': account_resp.data
                }

                apis = account_resp.data['apis']
                if 'calendar' in apis:
                    # Request to https://api.kloudless.com/account/me/cal/calendars/primary/events
                    primary_calendar_events = account.get(
                        'cal/calendars/primary/events'
                    )
                    resp_data['primary_calendar_events'] = (
                        primary_calendar_events.data)
                elif 'storage' in apis:
                    # Request to https://api.kloudless.com/account/me/storage/folders/root/contents
                    root_folder_contents = account.get(
                        'storage/folders/root/contents'
                    )
                    resp_data['root_folder_contents'] = root_folder_contents.data
            except APIException as e:
                self.http_json_response(e.status, e.error_data)
            else:
                self.http_json_response(200, resp_data)


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('app_id', type=str,
                        help='You can access app_id via https://developers.klo'
                             'udless.com/applications/*/details')
    parser.add_argument('api_key', type=str,
                        help='You can access api_key via https://developers.klo'
                             'udless.com/applications/*/details')
    parser.add_argument('--port', type=int, default=8020,
                        help='Port number to run the server, default to 8020')

    args = parser.parse_args()

    app_id = args.app_id
    api_key = args.api_key
    port = args.port

    print('Listening on localhost:%s' % port)
    httpd = HTTPServer(('', port), RequestHandler)
    httpd.serve_forever()
