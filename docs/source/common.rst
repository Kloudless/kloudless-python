Core Concepts
---------------

* You can make http requests with most classes in this library, like
  :class:`~kloudless.client.Client`, :class:`~kloudless.account.Account`,
  :class:`~kloudless.resources.base.Resource`,
  :class:`~kloudless.resources.base.ResourceList`, etc.

* Response data will be wrapped into the :class:`kloudless.resources.base.Response`
  and its subclass like :class:`kloudless.resources.base.ResponseJson`,
  :class:`~kloudless.resources.base.Resource` and
  :class:`~kloudless.resources.base.ResourceList`.

Logging Request Urls during Development
-----------------------------------------

You may find it useful to enable logging for every http request by setting the
log level to ``DEBUG``. It will print the exact http url being requested.

.. code:: python

    from kloudless.util import logger

    logger.setLevel('DEBUG')

Verifying the Bearer token
----------------------------

If the bearer token was transferred to the server from `Authenticator JS library 
<https://github.com/kloudless/authenticator.js>`_ or the client-side implicit 
grant flow, it's highly recommended that you verify the token.

.. code:: python

    from kloudless import verify_token
    from kloudless import exceptions

    app_id = "YOUR_APP_ID"
    token = "BEARER_TOKEN_TO_VERIFY"
    try:
        token_info = verify_token(app_id, token)
    except exceptions.TokenVerificationFailed:
        print("Token:{} does not belong to App:{}".format(token, app_id))
    except exceptions.APIException as e:
        # if other API request errors happened
        print(e.message)
    else:
        print(token_info)

Modifying Global Config
-------------------------

*  `base_url`: default to `https://api.kloudless.com`
*  `api_version`: default to `1`

.. code:: python

    from kloudless import configuration
    from kloudless import Account

    account = Account(token="YOUR_BEARER_TOKEN")
    print(account.url) # 'https://api.kloudless.com/v1/accounts/me'

    # Configuration changes would affect the Account and Client create afterward
    configuration['base_url'] = 'http://localhost:8002'
    configuration['api_version'] = '2'

    account = Account(token="YOUR_BEARER_TOKEN")
    print(account.url) # 'http://localhost:8002/v2/accounts/me'


Modifying API Version for One Request
---------------------------------------

You don't have to modify the global config if you only want to change the api
version for particular endpoints. The ``api_version`` parameter is available
for all http methods.

For more options available for http methods, see
:func:`kloudless.client.Session.request`.

.. code:: python

    from kloudless import Account

    account = Account(token="YOUR_BEARER_TOKEN")

    # Request to 'https://api.kloudless.com/v1/accounts/me'
    response = account.get()

    # Request to 'https://api.kloudless.com/v2/accounts/me'
    response = account.get(api_version=2)

Getting Upstream Raw Object
-----------------------------

If you want to access the ``raw`` object from the upstream service, please set
the ``get_raw_data`` parameter to ``True``. This is available for all http
methods.

For more options available for http methods, see
:func:`kloudless.client.Session.request`.

.. code:: python

    from kloudless import Account

    account = Account(token="BEARER_TOKEN_FOR_CALENDAR_SERVICE")

    calendar = account.get('cal/calendars/primary', get_raw_data=True)
    print(calendar.data['raw'])


Setting Default Headers for All Requests
------------------------------------------

Setting default headers for all requests is useful whenever you want to always
include raw data or make use of `user-impersonation <https://developers.kloudl
ess.com/docs/v1/core#api-wide-options-impersonating-a-user>`_.

.. code:: python

    from kloudless import Account

    account = Account(token='BEARER_TOKEN_FOR_CALENDAR_SERVICE')
    account.headers['X-Kloudless-Raw-Data'] = 'true'

    # the request afterward would include raw data by default
    calendars = account.get('cal/calendars')


Retrieving Events
-------------------
Once you `enable activity monitoring <https://developers.kloudless.com/account/
login?next=/applications/%2A/events-details>`_ for your application, you'll be
able to query for activity using our Events API. See `Events Documentation
<https://developers.kloudless.com/docs/latest/events#events>`_ for more
information.

.. code:: python

    from kloudless import Account

    account = Account(token="YOUR_BEARER_TOKEN")

    # You can skip this step by using the cursor you stored.
    cursor = account.get('events/latest').data['cursor']

    # Iterating all events through pages with page_size equals 50
    events = account.get('events', params={'cursor': cursor, 'page_size': 50})
    for event in events.get_paging_iterator():
        print(event.data)

    # You can store the latest cursor for next time usage
    latest_cursor = events.latest_cursor


Calling Upstream Service APIs
------------------------------

You can make requests to the upstream service API (a.k.a. pass-through requests)
by using :func:`kloudless.account.Account.raw`.

.. code:: python

    from kloudless import Account

    account = Account(token="'BEARER_TOKEN_FOR_GDRIVE_SERVICE'")

    # Using raw method to forward request to Google Drive API
    response = account.raw('GET', '/drive/v2/about')


Making Application Level Requests
----------------------------------

In rare cases, you may want to make requests in the application level.
You can make use of :class:`kloudless.client.Client` for requests.

.. code:: python

    from kloudless import Client

    # See https://developers.kloudless.com/docs/latest/meta#introduction-to-the-meta-api
    # Use meta bearer token to initialize Client
    meta_client = Client(token='YOUR_META_BEARER_TOKEN')

    # Get info of your applications
    applications = meta_client.get('meta/applications')
    print(applications.data)

    # Use API key to initialize Client
    client = Client(api_key='YOUR_API_KEY')

    # Get all accounts connect to your application
    accounts = client.get('accounts')
    print(accounts.data)