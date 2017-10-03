from .util import to_datetime, to_iso
from .http import request
from .exceptions import KloudlessException as KException
from . import config

import inspect
import json
import requests
import six
import warnings


class BaseResource(dict):

    # {'key': (serializer, deserializer)}
    _serializers = {
        'created': (to_iso, to_datetime),
        'modified': (to_iso, to_datetime),
        'expiration': (to_iso, to_datetime),
        'expiry': (to_iso, to_datetime),
        'token_expiry': (to_iso, to_datetime),
        'refresh_token_expiry': (to_iso, to_datetime),
        }

    _path_segment = None

    _parent_resource_class = None

    # requests.Session's connection pool could cause failures due to the lack
    # of keep-alives causing the connection to drop unexpectedly.
    # Use `requests` to be safe, but alter if better performance is preferable.
    _api_session = requests

    def __init__(self, id=None, parent_resource=None, configuration=None):
        if not configuration:
            configuration = {}
        self._configuration = config.merge(configuration)

        self['id'] = id

        # Saved state, as returned by the Kloudless API.
        self._previous_data = {}

        # Keys that used to be present that no longer are post-save.
        # Useful for more helpful error messages.
        self._removed_keys = set()

        self._parent_resource = parent_resource

        if self._parent_resource_class is not None:
            if self._parent_resource is None:
                raise KException(
                    "A %s object or ID must be specified as this "
                    "%s object's parent." %
                    (self._parent_resource_class,
                     self.__class__.__name__))

    def populate(self, data):
        """
        data: Response from Kloudless with data on this object.
        """
        removed = set(self.keys()) - set(data.keys())
        self._removed_keys |= removed

        id = self['id']
        self.clear()

        for k, v in data.items():
            if k in self._serializers:
                data[k] = self._serializers[k][1](v)

        for k, v in six.iteritems(data):
            super(BaseResource, self).__setitem__(
                k, self.__class__.create_from_data(
                    v, parent_resource=self._parent_resource,
                    configuration=self._configuration))

        if 'id' not in self:
            self['id'] = id

        # Update our state.
        self._previous_data = self.serialize(self)

    @classmethod
    def create_from_data(cls, data, parent_resource=None, configuration=None):
        if isinstance(data, list):
            return [cls.create_from_data(
                    d, parent_resource=parent_resource,
                    configuration=configuration) for d in data]
        elif isinstance(data, dict) and not isinstance(data, BaseResource):
            data = data.copy()

            klass = cls
            data_type = None
            if data.get('api') and data.get('type'):
                data_type = data['api'] + '_' + data['type']

            if data_type in resources:
                klass = resources[data_type]
            elif data.get('type') in resources:
                klass = resources[data['type']]

            instance = klass(id=data.get('id'),
                             parent_resource=parent_resource,
                             configuration=configuration)
            instance.populate(data)
            return instance
        else:
            return data

    @classmethod
    def serialize(cls, resource_data):
        """
        Converts values in the BaseResource object into primitive types.
        This helps convert the entire object to JSON.
        resource_data: Either the resource object, or a dict with the data
            to populate the resource.
        """
        serialized = {}
        for k, v in six.iteritems(resource_data):
            if isinstance(v, BaseResource):
                serialized[k] = v.serialize(v)
            elif k in cls._serializers:
                serialized[k] = cls._serializers[k][0](v)
            else:
                serialized[k] = v
        return serialized

    @classmethod
    def list_path(cls, parent_resource):
        raise NotImplementedError("Subclasses must implement list_path.")

    def detail_path(self):
        if not self['id']:
            raise KException("The detail_path cannot be obtained since the ID "
                             "is unknown.")
        return "%s/%s" % (self.list_path(self._parent_resource), self['id'])

    # Getter/Setter methods

    def __setattr__(self, k, v):
        if k[0] == '_' or k in self.__dict__:
            return super(BaseResource, self).__setattr__(k, v)
        else:
            self[k] = v

    def __getattr__(self, k):
        if k[0] == '_':
            raise AttributeError(k)
        try:
            return self[k]
        except KeyError as e:
            raise AttributeError(*e.args)

    def __setitem__(self, k, v):
        super(BaseResource, self).__setitem__(k, v)

    def __getitem__(self, k):
        try:
            return super(BaseResource, self).__getitem__(k)
        except KeyError:
            if k in self._removed_keys:
                raise KeyError(
                    "%r. The key %s was previously present but no longer is. "
                    "This is due to the object being updated with new "
                    "information returned from the Kloudless API, probably "
                    "due to the object being saved. Here are the current "
                    "attributes of this object: %s" %
                    (k, k, ', '.join(self.keys())))
            else:
                raise

    def __delitem__(self, k):
        raise TypeError(
            "Items cannot be deleted. Please set them to None instead if you "
            "wish to clear them.")


class AnnotatedList(list):
    """
    Given a deserialized response of all(), the objects returned by the API
    will be made iterable, and the other attributes will become attributes
    of this AnnotatedList object.
    """
    def __init__(self, all_data):
        if isinstance(all_data, list):
            return all_data

        objects = None
        for k, v in six.iteritems(all_data):
            if k in ['objects', 'permissions', 'properties'] and isinstance(v, list):
                objects = v
            else:
                setattr(self, k, v)

        if objects is None:
            raise KException("No lists were found!")
        list.__init__(self, objects)


def allow_proxy(func):
    func.allow_proxy = True
    return func


class ListMixin(object):
    @classmethod
    @allow_proxy
    def all(cls, parent_resource=None, configuration=None,
            headers=None, **params):
        response = request(cls._api_session.get,
                           cls.list_path(parent_resource),
                           configuration=configuration,
                           headers=headers, params=params)
        data = cls.create_from_data(
            response.json(), parent_resource=parent_resource,
            configuration=configuration)
        return AnnotatedList(data)


class RetrieveMixin(object):
    @classmethod
    @allow_proxy
    def retrieve(cls, id, parent_resource=None, configuration=None,
                 headers=None, **params):
        instance = cls(id=id, parent_resource=parent_resource,
                       configuration=configuration)
        response = request(cls._api_session.get, instance.detail_path(),
                           configuration=configuration,
                           headers=headers, params=params)
        instance.populate(response.json())
        return instance

    def refresh(self, headers=None):
        """
        Retrieves and sets new metadata for the resource.
        """
        response = request(self._api_session.get, self.detail_path(),
                           configuration=self._configuration,
                           headers=headers)
        self.populate(response.json())


class ReadMixin(RetrieveMixin, ListMixin):
    pass


class CreateMixin(object):
    @classmethod
    @allow_proxy
    def create(cls, data=None, params=None, method='post',
               parent_resource=None, configuration=None, headers=None):
        """
        params: A dict containing query parameters.
        data: A dict containing data.
        """
        method = getattr(cls._api_session, method)

        if not data:
            data = {}

        if type(data) in [list, tuple]:
            data = [cls.serialize(data_obj) for data_obj in data]
        else:
            data = cls.serialize(data)

        if not params:
            params = {}
        response = request(method, cls.list_path(parent_resource),
                           configuration=configuration, headers=headers,
                           data=data, params=params)
        return cls.create_from_data(
            response.json(), parent_resource=parent_resource,
            configuration=configuration)


class UpdateMixin(object):
    def _data_to_save(self, new_data):
        """
        Override this for any specific checks or additions to data.
        """
        return new_data

    def save(self, headers=None, **params):
        data = self.serialize(self)

        new_data = {}
        for k, v in six.iteritems(data):
            if k not in self._previous_data or self._previous_data[k] != v:
                # Attribute is new or was updated
                new_data[k] = v

        new_data = self._data_to_save(new_data)

        if new_data:
            if self['id'] is None:
                if hasattr(self.__class__, 'create'):
                    raise KException("No ID provided. Use create() to create "
                                     "new resources instead.")
                else:
                    raise KException("No ID provided to identify the resource "
                                     "to update.")
            response = request(self._api_session.patch, self.detail_path(),
                               configuration=self._configuration,
                               headers=headers, data=new_data,
                               params=params)
            self.populate(response.json())

            # For some resources (eg: File/Folder), the parent resource could
            # be different. Check for that.
            # This assumes that if the metadata contains an 'account' key,
            # it maps to the correct Account ID. We update our parent
            # resource with the ID and it's metadata if it is different.
            res_type = resource_types[self.__class__]
            if (self._parent_resource and res_type in ['file', 'folder', 'link']):
                parent_res_type = resource_types[self._parent_resource_class]
                if (hasattr(self, parent_res_type) and
                        self._parent_resource.id != self[parent_res_type]):
                    self._parent_resource.id = self[parent_res_type]
                    self._parent_resource.refresh()

            return True
        return False


class DeleteMixin(object):
    def delete(self, headers=None, **params):
        request(self._api_session.delete, self.detail_path(),
                configuration=self._configuration,
                headers=headers, params=params)
        self.populate({})


class CopyMixin(object):
    def _copy(self, headers=None, **data):
        """
        Copy the file/folder to another location.
        """
        response = request(self._api_session.post,
                           "%s/copy" % self.detail_path(),
                           configuration=self._configuration,
                           headers=headers, data=data)
        return self.__class__.create_from_data(
            response.json(), parent_resource=self._parent_resource,
            configuration=self._configuration)


class WriteMixin(CreateMixin, UpdateMixin, DeleteMixin):
    pass


class ResourceProxy(object):
    """
    Create a proxy object. Whenever a function is called on it
    that is present on the underlying model, we attempt to call
    the underlying model. This is useful because resources can add in
    parameters like the parent_resource if it has not been specified yet.
    The Account resource does this.
    """

    def __init__(self, klass, parent_resource=None, configuration=None):
        self.klass = klass
        self.parent_resource = parent_resource
        self.configuration = configuration

    def __getattr__(self, name):
        method = getattr(self.klass, name, None)

        def proxy_method(self, *args, **kwargs):
            self.update_kwargs(kwargs)
            return method(*args, **kwargs)

        if inspect.ismethod(method):
            if getattr(method, 'allow_proxy', False):
                return proxy_method.__get__(self)
            else:
                return method
        else:
            raise AttributeError(name)

    def __call__(self, *args, **kwargs):
        self.update_kwargs(kwargs)
        return self.klass(*args, **kwargs)

    def update_kwargs(self, kwargs):
        if 'parent_resource' not in kwargs:
            kwargs['parent_resource'] = self.parent_resource
        if 'configuration' not in kwargs:
            kwargs['configuration'] = self.configuration


class Proxy:
    def _get_proxy(self, resource_name):
        if not getattr(self, '_proxies', None):
            setattr(self, '_proxies', {})

        resource = resources[resource_name]
        if self._proxies.get(resource_name) is None:
            self._proxies[resource_name] = ResourceProxy(
                resource, parent_resource=self,
                configuration=self._configuration)
        return self._proxies[resource_name]


class Account(BaseResource, ReadMixin, WriteMixin, Proxy):
    def __init__(self, *args, **kwargs):
        super(Account, self).__init__(*args, **kwargs)

    @classmethod
    def list_path(cls, parent_resource):
        return 'accounts'

    @classmethod
    def serialize_account(cls, resource_data):
        account_properties = ['active', 'account', 'service', 'token',
                              'token_secret', 'refresh_token', 'token_expiry',
                              'refresh_token_expiry']
        serialized = {}
        for k, v in six.iteritems(resource_data):
            if isinstance(v, BaseResource):
                serialized[k] = v.serialize_account(v)
            elif k not in account_properties:
                continue
            elif k in cls._serializers:
                serialized[k] = cls._serializers[k][0](v)
            else:
                serialized[k] = v
        return serialized

    def save(self, headers=None, **params):
        # TODO: add in fields token, token_secret, refresh_token
        request(self._api_session.patch, self.detail_path(),
                configuration=self._configuration, headers=headers,
                data=self.serialize_account(self), params=params)

    def convert(self, headers=None, data=None, params=None):
        # Deprecated in favor of encode_raw_id

        params = {} if params is None else params
        data = {} if data is None else data

        convert_path = "%s/%s" % (self.detail_path(), 'storage/convert_id')

        response = request(self._api_session.post, convert_path,
                           configuration=self._configuration,
                           headers=headers, data=data, params=params)

        return response.json()

    def encode_raw_id(self, data=None, params=None, headers=None):
        path = "%s/encode_raw_id" % self.detail_path()
        return request(
            self._api_session.post, path, data=data or {}, params=params or {},
            headers=headers, configuration=self._configuration).json()

    def raw(self, raw_uri='', raw_method='GET', data=None, params=None,
            headers=None):
        """
        raw_uri: Upstream URI to make the pass-through API request to.
        raw_method: HTTP Method to make the pass-through request with.
        params: A dict containing query parameters.
        data: A dict containing data.
        """
        data = data or {}
        params = params or {}
        headers = headers or {}

        headers['X-Kloudless-Raw-URI'] = raw_uri
        headers['X-Kloudless-Raw-Method'] = raw_method

        return request(
            self._api_session.post, "%s/raw" % self.detail_path(), data=data,
            headers=headers, params=params, configuration=self._configuration)


    @property
    def links(self):
        return self._get_proxy('link')

    @property
    def files(self):
        return self._get_proxy('file')

    @property
    def folders(self):
        return self._get_proxy('folder')

    @property
    def search(self):
        return self._get_proxy('search')

    @property
    def recent(self):
        return self._get_proxy('recent')

    @property
    def calendars(self):
        return self._get_proxy('calendars')

    @property
    def events(self):
        return self._get_proxy('events')

    @property
    def multipart(self):
        return self._get_proxy('multipart')

    @property
    def users(self):
        return self._get_proxy('user')

    @property
    def groups(self):
        return self._get_proxy('group')

    @property
    def crm_objects(self):
        return self._get_proxy('crm_object')

    @property
    def crm_accounts(self):
        return self._get_proxy('crm_account')

    @property
    def crm_contacts(self):
        return self._get_proxy('crm_contact')

    @property
    def crm_leads(self):
        return self._get_proxy('crm_lead')

    @property
    def crm_opportunities(self):
        return self._get_proxy('crm_opportunity')

    @property
    def crm_campaigns(self):
        return self._get_proxy('crm_campaign')

    @property
    def crm_tasks(self):
        return self._get_proxy('crm_task')

    @property
    def crm_batch(self):
        return self._get_proxy('crm_batch')

    @property
    def crm_recent(self):
        return self._get_proxy('crm_recent')

    @property
    def crm_search(self):
        return self._get_proxy('crm_search')

    @property
    def crm_events(self):
        return self._get_proxy('crm_events')


class AccountBaseResource(BaseResource):
    _parent_resource_class = Account

    def __init__(self, *accounts, **kwargs):
        """
        accounts should only be a list with 1 account in it.
        """
        if accounts:
            kwargs['parent_resource'] = accounts[0]
        super(AccountBaseResource, self).__init__(**kwargs)

    @classmethod
    def list_path(cls, account):
        account_path = account.detail_path()
        return "%s/%s" % (account_path, cls._path_segment)


class FileSystem(BaseResource, Proxy):
    _path_segment = None

    @property
    def permissions(self):
        return self._get_proxy('permission')


class FileSystemBaseResource(BaseResource):
    _parent_resource_class = FileSystem

    def __init__(self, *files, **kwargs):
        if files:
            kwargs['parent_resource'] = files[0]
        super(FileSystemBaseResource, self).__init__(**kwargs)

    @classmethod
    def list_path(cls, file):
        file_path = file.detail_path()
        return "%s/%s" % (file_path, cls._path_segment)


class File(AccountBaseResource, RetrieveMixin, DeleteMixin, UpdateMixin,
           CopyMixin, FileSystem):
    _path_segment = 'storage/files'

    @property
    def properties(self):
        return self._get_proxy('property')

    @classmethod
    @allow_proxy
    def create(cls, file_name='', parent_id='root', file_data='', params=None,
               headers=None, parent_resource=None, configuration=None):
        """
        This handles file uploads.
        `file_data` can be either a string with file data in it or a
        file-like object.
        """
        all_headers = {
            'X-Kloudless-Metadata': json.dumps({
                'name': file_name,
                'parent_id': parent_id,
            }),
            'Content-Type': 'application/octet-stream',
        }
        all_headers.update(headers or {})

        response = request(cls._api_session.post, cls.list_path(parent_resource),
                           data=file_data, params=params, headers=all_headers,
                           configuration=configuration)
        return cls.create_from_data(
            response.json(), parent_resource=parent_resource,
            configuration=configuration)

    def update(self, file_data='', params=None, headers=None):
        """
        This overwites the file specified by 'file_id' with the contents of
        `file_data`.
        `file_data` can be either a string with file data in it or a
        file-like object.
        """
        headers = headers or {}
        headers.setdefault('Content-Type', 'application/octet-stream')

        response = request(self._api_session.put, self.detail_path(),
                           data=file_data, params=params, headers=headers,
                           configuration=self._configuration)
        self.populate(response.json())
        return True

    def contents(self, headers=None):
        """
        This handles file downloads. It returns a requests.Response object
        with contents:

            from contextlib import closing

            with closing(account.files(id=file_id).contents()) as r:
                # Do things with response here
                data = r.content

        For more information, see the documentation for requests.Response's
        Body content workflow.
        """
        response = request(self._api_session.get,
                           "%s/contents" % self.detail_path(),
                           configuration=self._configuration,
                           headers=headers, stream=True)
        return response

    def copy_file(self, headers=None, **data):
        return self._copy(headers=headers, **data)

    @classmethod
    @allow_proxy
    def upload_url(cls, data=None, params=None,
                   parent_resource=None, configuration=None, headers=None):
        upload_url_path = "%s/%s" % (cls.list_path(parent_resource), 'upload_url')
        response = request(cls._api_session.post, upload_url_path,
                           configuration=configuration, data=data or {},
                           params=params or {}, headers=headers)
        return response.json()


class Folder(AccountBaseResource, RetrieveMixin, DeleteMixin, UpdateMixin,
             CreateMixin, CopyMixin, FileSystem):

    _path_segment = 'storage/folders'

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('id', 'root')
        super(Folder, self).__init__(*args, **kwargs)

    def contents(self, headers=None):
        response = request(self._api_session.get,
                           "%s/contents" % self.detail_path(),
                           configuration=self._configuration,
                           headers=headers)
        data = self.create_from_data(
            response.json(), parent_resource=self._parent_resource,
            configuration=self._configuration)
        return AnnotatedList(data)

    def copy_folder(self, headers=None, **data):
        return self._copy(headers=headers, **data)


class Link(AccountBaseResource, ReadMixin, WriteMixin):
    _path_segment = 'storage/links'


class Search(AccountBaseResource, ListMixin):
    _path_segment = 'storage/search'


class Recent(AccountBaseResource, ListMixin):
    _path_segment = 'storage/recent'


class Calendar(AccountBaseResource, ReadMixin, WriteMixin, Proxy):
    _path_segment = 'cal/calendars'

    @property
    def events(self):
        return self._get_proxy('calendar_events')


class CalendarEvents(Calendar):
    _path_segment = 'events'


class Events(AccountBaseResource, ListMixin):
    _path_segment = 'events'

    @classmethod
    @allow_proxy
    def latest_cursor(cls, parent_resource=None, configuration=None,
                      headers=None):
        response = request(cls._api_session.get,
                           "%s/latest" % cls.list_path(parent_resource),
                           configuration=configuration, headers=headers)
        data = response.json()
        if 'cursor' in data:
            return data['cursor']
        else:
            return data


class Multipart(AccountBaseResource, RetrieveMixin, CreateMixin, DeleteMixin):
    """
    Multipart Uploads.
    Create the multipart upload first, prior to uploading chunks of data.
    Complete the upload once all chunks have been uploaded.
    """
    _path_segment = 'storage/multipart'

    def upload_chunk(self, part_number=None, data='',
                     parent_resource=None, configuration=None,
                     headers=None, **params):
        """
        This handles uploading chunks of the file, after a multipart upload has
        been initiated.
        `part_number`
        `data` can be either a string with file data in it or a
        file-like object.
        """
        params.update({'part_number': part_number})

        headers = headers or {}
        headers.setdefault('Content-Type', 'application/octet-stream')

        request(self._api_session.put, self.detail_path(),
                data=data, params=params, headers=headers,
                configuration=configuration)
        return True

    def complete(self, headers=None, **params):
        """
        Completes the multipart upload and returns a File object.
        """
        response = request(self._api_session.post,
                           "%s/complete" % self.detail_path(),
                           params=params, configuration=self._configuration,
                           headers=headers)
        return File.create_from_data(
            response.json(), parent_resource=self._parent_resource,
            configuration=self._configuration)


class Permission(FileSystemBaseResource, ListMixin, CreateMixin):
    _path_segment = 'permissions'

    @classmethod
    @allow_proxy
    def all(cls, parent_resource=None, configuration=None,
            headers=None, **params):
        response = request(cls._api_session.get,
                           cls.list_path(parent_resource),
                           configuration=configuration, headers=headers,
                           params=params)

        response_json = response.json()
        permissions = response_json.get('permissions')
        for perm in permissions:
            perm['type'] = 'permission'
        response_json['permissions'] = permissions
        data = cls.create_from_data(
            response_json, parent_resource=parent_resource,
            configuration=configuration)
        return AnnotatedList(data)

    @classmethod
    @allow_proxy
    def create(cls, params=None, parent_resource=None, configuration=None,
               data=None, headers=None):
        return super(Permission, cls).create(params=params,
                                             parent_resource=parent_resource,
                                             configuration=configuration,
                                             method='put', data=data,
                                             headers=headers)

    @classmethod
    @allow_proxy
    def update(cls, params=None, parent_resource=None, configuration=None,
               data=None, headers=None):
        return super(Permission, cls).create(params=params,
                                             parent_resource=parent_resource,
                                             configuration=configuration,
                                             method='patch', data=data,
                                             headers=headers)


class Property(FileSystemBaseResource, ListMixin, CreateMixin):
    _path_segment = 'properties'

    @classmethod
    @allow_proxy
    def update(cls, parent_resource=None, configuration=None, headers=None,
               data=None, **params):
        """
        Updates custom properties associated with this file.
        'data' should be a list of dicts containing key/value pairs.
        """
        return super(Property, cls).create(params=params,
                                           parent_resource=parent_resource,
                                           configuration=configuration,
                                           method='patch', data=data,
                                           headers=headers)

    @classmethod
    @allow_proxy
    def delete_all(cls, parent_resource=None, configuration=None,
                   headers=None):
        """
        Deletes all custom properties associated with this file.
        """
        request(cls._api_session.delete, cls.list_path(parent_resource),
                configuration=configuration, headers=headers)
        return True


class User(AccountBaseResource, ReadMixin):
    _path_segment = 'team/users'

    def get_groups(self, headers=None, **params):
        response = request(self._api_session.get, "%s/%s" %
                           (self.detail_path(), "memberships"),
                           configuration=self._configuration,
                           headers=headers, params=params)

        data = Group.create_from_data(
            response.json(), parent_resource=self._parent_resource,
            configuration=self._configuration)
        return AnnotatedList(data)


class Group(AccountBaseResource, ReadMixin):
    _path_segment = 'team/groups'

    def get_users(self, headers=None, **params):
        response = request(self._api_session.get, "%s/%s" %
                           (self.detail_path(), "members"),
                           configuration=self._configuration,
                           headers=headers, params=params)

        data = User.create_from_data(
            response.json(), parent_resource=self._parent_resource,
            configuration=self._configuration)
        return AnnotatedList(data)


class CRMObject(AccountBaseResource, ListMixin, CreateMixin, RetrieveMixin,
                UpdateMixin, DeleteMixin):
    _path_segment = 'crm/objects'
    raw_type = None

    def __init__(self, *args, **kwargs):
        super(CRMObject, self).__init__(*args, **kwargs)

    @classmethod
    @allow_proxy
    def all(cls, parent_resource=None, configuration=None,
            headers=None, **params):
        if cls.raw_type is not None:
            params['raw_type'] = cls.raw_type
        return super(CRMObject, cls).all(parent_resource=parent_resource,
                                         configuration=configuration,
                                         headers=headers, **params)

    @classmethod
    @allow_proxy
    def create(cls, params=None, parent_resource=None, configuration=None,
               headers=None, method='post', data=None):
        params = {} if params is None else params
        if cls.raw_type is not None:
            params['raw_type'] = cls.raw_type
        return super(CRMObject, cls).create(params=params,
                                            parent_resource=parent_resource,
                                            configuration=configuration,
                                            headers=headers,
                                            method=method, data=data)

    @classmethod
    @allow_proxy
    def retrieve(cls, id, parent_resource=None, configuration=None,
                 headers=None, **params):
        if cls.raw_type is not None:
            params['raw_type'] = cls.raw_type
        return super(CRMObject, cls).retrieve(id,
                                              parent_resource=parent_resource,
                                              configuration=configuration,
                                              headers=headers,
                                              **params)

    def save(self, **params):
        # TODO: change serializer
        if self.raw_type is not None:
            params['raw_type'] = self.raw_type
        super(CRMObject, self).save(**params)

    def delete(self, **params):
        if self.raw_type is not None:
            params['raw_type'] = self.raw_type
        super(CRMObject, self).delete(**params)


class CRMAccount(CRMObject):
    _path_segment = 'crm/accounts'
    raw_type = 'Account'


class CRMContact(CRMObject):
    _path_segment = 'crm/contacts'
    raw_type = 'Contact'


class CRMLead(CRMObject):
    _path_segment = 'crm/leads'
    raw_type = 'Lead'


class CRMOpportunity(CRMObject):
    _path_segment = 'crm/opportunities'
    raw_type = 'Opportunity'


class CRMCampaign(CRMObject):
    _path_segment = 'crm/campaigns'
    raw_type = 'Campaign'


class CRMTask(CRMObject):
    _path_segment = 'crm/tasks'
    raw_type = 'Task'


class CRMBatchRequest(AccountBaseResource, CreateMixin):
    _path_segment = 'crm/batch'


class CRMSearch(AccountBaseResource, ListMixin):
    _path_segment = 'crm/search'


class Application(BaseResource, ReadMixin, WriteMixin, Proxy):

    def __init__(self, *args, **kwargs):
        super(Application, self).__init__(*args, **kwargs)

    @classmethod
    def list_path(cls, parent_resource):
        return 'applications'

    @property
    def apikeys(self):
        return self._get_proxy('apikey')

    @property
    def webhooks(self):
        return self._get_proxy('webhook')


class ApplicationBaseResource(BaseResource):
    _parent_resource_class = Application

    def __init__(self, *applications, **kwargs):
        if applications:
            kwargs['parent_resource'] = applications[0]
        super(ApplicationBaseResource, self).__init__(**kwargs)

    @classmethod
    def list_path(cls, application):
        application_path = application.detail_path()
        return "%s/%s" % (application_path, cls._path_segment)


class ApiKey(ApplicationBaseResource, ListMixin, CreateMixin, DeleteMixin):
    _path_segment = 'apikeys'

    def detail_path(self):
        if not self['key']:
            raise KException("The detail_path cannot be obtained since the key"
                             " is unknown.")
        return "%s/%s" % (self.list_path(self._parent_resource), self['key'])


class WebHook(ApplicationBaseResource, ListMixin, CreateMixin, RetrieveMixin,
              DeleteMixin):
    _path_segment = 'webhooks'

    def detail_path(self):
        if not self['id']:
            raise KException("The detail_path cannot be obtained since the id "
                             "is unknown.")
        return "%s/%s" % (self.list_path(self._parent_resource), self['id'])

resources = {
    'account': Account,
    'file': File,
    'folder': Folder,
    'link': Link,
    'search': Search,
    'recent': Recent,
    'calendars': Calendar,
    'calendar_events': CalendarEvents,
    'events': Events,
    'multipart': Multipart,
    'permission': Permission,
    'property': Property,
    'user': User,
    'group': Group,
    # CRM Endpoint
    'crm_object': CRMObject,
    'crm_account': CRMAccount,
    'crm_contact': CRMContact,
    'crm_lead': CRMLead,
    'crm_opportunity': CRMOpportunity,
    'crm_campaign': CRMCampaign,
    'crm_task': CRMTask,
    'crm_batch': CRMBatchRequest,
    'crm_search': CRMSearch,
    # Application Endpoint
    'application': Application,
    'apikey': ApiKey,
    'webhook': WebHook,
}
resource_types = {v: k for k, v in six.iteritems(resources)}
