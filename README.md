Python library for the Kloudless API
=====================================

Python library for the [Kloudless API](https://developers.kloudless.com).

## Installation

To install, clone the repository and run:

```bash
python setup.py install
```

You may also install via pip:

```bash
pip install https://github.com/kloudless/kloudless-python/archive/master.zip
```

## Documentation

See the [Kloudless API Docs](https://developers.kloudless.com/docs) for the official reference.
You can obtain an API Key at the [Developer Portal](https://developers.kloudless.com), or
use an authenticated user's Bearer token.

## Configuration

Configure Kloudless using the `configure` method on the `kloudless` module:

```python
>>> import kloudless
>>> kloudless.configure(token="BEARER TOKEN")
>>> # Or:
>>> kloudless.configure(api_key="API_KEY")
```

Here are the configuration options:

* `api_key` The Kloudless API Key. Will be used instead of the Bearer Token if
  both are provided.
* `dev_key` The Kloudless Developer Key. Used to access the Management API.
* `token` A Kloudless account's Bearer token.
* `api_version` The API version. (default: `0`)
* `base_url` The API Server's URL. (default: `https://api.kloudless.com`)
* `throttle_retry_strategy`: Defaults to retrying a request with exponential fallback
  if it is rate-limited, or by checking the Retry-After header in the response.
  Set to `None` to never retry. You can also set this to your own sub-class to
  handle retries in some custom manner. See `throttling.py` for more information.
* `headers`: A dictionary of headers to send on every request. Headers included
  on individual requests will take precedence. See `config.py` for some examples.

### Resources

Here are some of the popular resource classes available:

* `Account`
* `File`
* `Folder`
* `Link`
* `Search`
* `Recent`
* `Events`
* `Multipart`
* `Property`
* `Permission`
* `CRMObject`

A full list can be viewed in [resources.py](https://github.com/Kloudless/kloudless-python/blob/master/kloudless/resources.py).

Each class has the following methods where applicable:

* `create(**data)` makes a POST request to create a resource of that type.
* `all(**params)` makes a GET request to list all resources
* `retrieve(id, **params)` makes a GET request to retrieve metadata for that resource.

In addition, instances have the methods below where applicable:

* `save(**params)` makes a PATCH request to update the resource after attributes on it
  have been modified.
* `delete(**params)` makes a DELETE request to delete the resource.

Parameters mentioned above:

* `id`: The ID of the resource.
* `params`: Keyword arguments that will be converted into query parameters for the request.
* `data`: Keyword arguments that will be converted into a JSON string sent in the body of the request.

#### Accessing nested resources

The `Account` model has some helper attributes to make using class methods easier. For example:

* `links` references the Link class
* `files` references the File class
* `folders` references the Folder class
* `search` references the Search class
* `recent` references the Recent class
* `events` references the Events class
* `multipart` references the Multipart class
* `calendars` references the Calendar class

A full list can be viewed under the `Account` class in [resources.py](https://github.com/Kloudless/kloudless-python/blob/master/kloudless/resources.py).

## Examples

### Basics

Here is an example retrieving metadata on a folder in an account:

```python
>>> import kloudless; kloudless.configure(api_key="API_KEY")
>>> accounts = kloudless.Account.all()
>>> account = accounts[0]
>>> root_folder = account.folders()
>>> children = root_folder.contents()
>>> child_folder = [f for f in children if f.type == 'folder'][0]
```

The shortcut method `account.folders` is used above,
but you can also instantiate the classes above independently:

```python
>>> root_folder = kloudless.Folder(id='root', parent_resource=account)
```

There are different ways to retrieve information on a resource, given it's ID.
Here are some examples, given `account_id` and `child_folder_id` as the account and
folder IDs respectively.

```python
# We need to create the account object with an account ID first.
>>> account = kloudless.Account(id=account_id)

# Get the child folder via the "account.folders" helper method.
>>> account.folders.retrieve(id=child_folder_id)

# Retrieve the child folder a different way
>>> kloudless.Folder.retrieve(id=child_folder.id, parent_resource=account)

# Retrieve the child folder another way
>>> f = kloudless.Folder(id=child_folder.id, parent_resource=account)
>>> f.refresh() # Pulls latest metadata given the ID.
```

Another example retrieving link information a few different ways:

```python
# A few different ways
>>> link = kloudless.Link.all(parent_resource=account)[0]
>>> link = account.links.retrieve(id=link.id)
>>> link = kloudless.Link.retrieve(id=link.id, parent_resource=account)
>>> link = kloudless.Link(id=link.id); link.refresh();
```

### Moving a file

Here's an example moving a file from one account to a folder in a different account.

```python
# Get two cloud storage accounts.
>>> accounts = kloudless.Account.all();
>>> accounts[0].id
10
>>> accounts[1].id
20

# Find a file in the first account.
>>> root_contents = accounts[0].folders().contents() # Get the root folder contents
>>> f = [f for f in root_contents if f.type == 'file'][0] # Get a file

# Find a folder in the second account.
>>> root_contents = accounts[1].folders().contents()
>>> folder = [folder for folder in root_contents if folder.type == 'folder'][0]

# Update the file with new information
>>> f.account = accounts[1].id # Moving it to a different account
>>> f.name = 'new file name.txt'
>>> f.parent_id = folder.id
>>> f.save() # Makes the request to move the file.

# 'f' now represents the new file object.
```

### Calendar API

Here is an example calendar and calendar events in an account:

```python
>>> import kloudless; kloudless.configure(api_key="API_KEY")
>>> accounts = kloudless.Account.all()
>>> account = accounts[0]
>>> calendars = account.calendars.all()

# Creating a calendar in an account
>>> calendar_data = {
....    "name": "My Test Calendar",
....    "description": "A test calendar for testing",
....    "location": "San Francisco, CA",
....    "timezone": "US/Pacific"
....}
>>> calendar = account.calendars.create(data=calendar_data)

# Retrieving a calendar in an account
>>> calendar = account.calendars.retrieve(id=calendar_id)

# Updating the calendar with new information
>>> calendar.name = "New Calendar name"
>>> calendar.description = "New Calendar description"
>>> calendar.save() # Makes the request to update the calendar.

# Deleting a calendar
>>> calendar.delete()

# Retrieving a list of calendar events
>>> events = calendar.events.all()

# Creating a calendar event
>>> event_data = {
....    "name": "Event 2",
....    "start": "2017-09-01T12:30:00Z",
....    "end": "2017-09-01T13:30:00Z",
....    "creator": {
....        "name": "Company Owner",
....        "email": "owner@company.com"
....    },
....    "owner": {
....        "name": "Company Owner",
....        "email": "owner@company.com"
....    }
....}
>>> event = calendar.events.create(data=event_data)

# Retrieving a calendar event
>>> event = calendar.events.retrieve(id=event_id)

# Updating the calendar event with new information
>>> event.name = "Event 2 Update"
>>> event.start = "2017-09-01T12:00:00Z"
>>> event.end = "2017-09-01T13:00:00Z"
>>> event.save() # Makes the request to update the calendar event.

# Deleting a calendar
>>> event.delete()
```

## Apps using the Python SDK

* https://github.com/vinodc/cloud-text-editor creates folders and uploads files via the Kloudless API.

## Tests
To install test dependencies, run `pip install -r tests/requirements.txt`.

The tests are written using [py.test](http://pytest.org) and can be run like so
(from within this directory):
```shell
pip install tox
tox
```
#### Integration Tests

Integration tests are seperate and can be run collectively or independently
within the `tests/integration/` directory, with an appropriate `API_KEY` set
in the environment. Here is a full list of environment variables that can
be used to configure the tests:

`API_KEY`: Required. The API Key to use.

`DEV_KEY`: Required if testing the Management API. The Developer Key to use.

`BASE_URL`: Optional. Defaults to 'https://api.kloudless.com'. Configures the
    base URL to use for tests.

`SERVICES`: Optional. A comma-separated list of service names to restrict the
    services tested.

`ACCOUNTS`: Optional. A comma-separated list of account IDs to restrict the
    accounts tested.

`REQUESTS_CA_BUNDLE`: Optional. If pointing to a BASE_URL secured with a
    non-trusted root CA certificate, this environment variable can be pointed
    to the certificate to trust.
    See http://docs.python-requests.org/en/latest/user/advanced/#ssl-cert-verification
    for more information.

`RUN_LONG_TESTS`: Optional. Defaults to a Falsey value. If Truthy, tests which
    take an extended period of time to run (due to waiting/sleeping), will be
    included.

Examples:

```shell
API_KEY='...' python test.py
API_KEY='...' python test_cases/test_link.py
API_KEY='...' SERVICES='dropbox' python test_cases/test_link.py
API_KEY='...' SERVICES='dropbox,s3,box' python test.py
DEV_KEY='...' BASE_URL='...' python management_api/test_application.py
API_KEY='...' DEV_KEY='...' BASE_URL='...' python test.py
```

An account for each service will be obtained from the API to run tests for.

## Acknowledgements

* [requests](https://github.com/kennethreitz/requests) makes the API requests easy.
* [stripe-python](https://github.com/stripe/stripe-python) was a useful resource while researching the interface for this API.
