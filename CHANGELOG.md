# Change Log

## 1.1.0

#### New Features
* Python 3 support added.

#### Bug-fixes
* AccountKey references removed.
* Improving permissions endpoint compatibility with services like Google Drive.

## 1.0.0

* The API version has been updated to `v1`. This introduces backwards
  incompatible changes. Please review the
  [migration guide](https://developers.kloudless.com/docs/v1/migration)
  for more information on migrating from `v0` to `v1`.

### Backwards-incompatible SDK changes

* The `create()` method requires all data attributes to be provided via a
  dictionary passed in through the `data` keyward argument rather than via
  arbitrary keyword arguments. This may vary based on specific implementations,
  such as for file uploads via `File.create()`.

* The `File` class's `create()` method requires all query parameters to be
  provided via a dictionary passed in through the `params` keyward argument
  rather than via arbitrary keyword arguments.

* The `Account.file_upload_url` instance method has been moved to be a
  class method at `File.upload_url` instead.
