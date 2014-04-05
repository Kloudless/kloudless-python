Python library for the Kloudless API
=====================================

Python library for the [Kloudless API](https://developers.kloudless.com).
This is in beta and under significant development.

## Installation

To install, clone the repository and run:

```bash
python setup.py install
```

## Documentation

See the [Kloudless API Docs](https://developers.kloudless.com/docs) for the official reference.
You can obtain an API Key at the [Developer Portal](https://developers.kloudless.com).

There are four models:

* `Account`
* `File`
* `Folder`
* `Link`
 
Each class have the following methods where applicable:

* `create(**params)` makes a POST request to create a resource of that type.
* `all(**params)` makes a GET request to list all resources
* `retrieve(id, **params)` makes a GET request to retrieve metadata for that resource.

In addition, instances have the methods below where applicable:

* `save()` makes a PATCH request to update the resource after attributes on it
  have been modified.
* `delete(**params)` makes a DELETE request to delete the resource.

The `Account` model has some helper attributes to make using class methods easier:

* `links` references the Link class
* `files` references the File class
* `folders` references the Folder class

Here is an example retrieving metadata on a folder in an account:

```python
>>> import kloudless; kloudless.configure(api_key="API_KEY")
>>> accounts = kloudless.Account.all()
>>> account = accounts[0]
>>> root_folder = account.folders()
>>> children = root_folder.contents()
>>> child_folder = [f for f in children if f.type == 'folder'][0]

# Retrieve the child folder again
>>> account.folders.retrieve(id=child_folder.id)

# Retrieve the child folder a different way
>>> kloudless.Folder.retrieve(id=child_folder.id, parent_resource=account)
```

## Examples using the Python SDK

* https://github.com/vinodc/cloud-text-editor creates folders and uploads files via the Kloudless API.

## TODO

* Tests!
* Flesh out documentation.
* Distribute via package server.
* Fix moving files/folders between folders.

## Acknowledgements

* [requests](https://github.com/kennethreitz/requests) makes the API requests easy.
* [stripe-python](https://github.com/stripe/stripe-python) was a useful resource while researching the interface for this API.

