How to Run the Demo Server
======================

The Kloudless demo server serves as an example to demonstrate how the Kloudless 
library can help with OAuth authorization flow.

## Installation 

Install from source to get `demo_server.py` file.

## Add callback url

Navigate to [App Details page](https://developers.kloudless.com/applications/*/details#oauth-settings).

Add `http://localhost:8020/callback` to OAuth settings. 

![Add Redirect URI](/docs/source/_static/redirect_uri_input.png)

## Get App ID and API Key

Navigate to [App Details page](https://developers.kloudless.com/applications/*/details).

App ID and API Key can be copied from the text input.

![Get APP ID and API Key](/docs/source/_static/app_id_and_api_key_input.png)

## Run the Demo Server

Paste your APP ID and API Key in and run the following command.
```bash
python examples/demo_server.py YOUR_APP_ID YOUR_API_KEY
```

The demo server runs at port 8020 by default. You can change the port
 by adding  `--port YOUR_PORT_NUMBER` while running the command above.

If you decide not to use the default and instead specify a different port, 
be sure to update callback url to the new port as well. See [Add callback url](#add-callback-url) above.

## Visit the demo page

Navigate to [http://localhost:8020](http://localhost:8020).

You can connect either storage service account to retrieve root folder contents
or calendar service account to retrieve primary calendar's events.

Also check `demo_server.py` to see how `kloudless.get_authorization_url` and
 `kloudless.get_token_from_code` could help you with the authorization flow.
