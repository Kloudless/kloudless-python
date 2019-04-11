from __future__ import unicode_literals

from six.moves.urllib.parse import parse_qs, urlparse, urlunparse

from .. import exceptions
from ..re_patterns import (events_pattern, full_account_pattern,
                           primary_calendar_alias)
from ..util import url_join


class Empty(object):
    """
    Used to represent empty attribute.
    This is needed because None is used to represent null in json
    """
    def __bool__(self):
        return False

    __nonzero__ = __bool__


empty = Empty()  # create instance to make __bool__ take effect


class Response(object):
    """
    Base Response class for this library.

    **Instance attributes**

    :ivar str url: Base url which would be used as prefix for all http method
        calls

    :ivar dict query_params: Query parameter from request

    :ivar client: :class:`kloudless.client.Client` or
        :class:`kloudless.account.Account`

    :ivar response: :class:`requests.Response` if available
    """
    def __init__(self, client, url, response=None):

        parse_result = urlparse(url)
        # clean up the url to make url_join work
        self.url = urlunparse(parse_result._replace(query=''))
        self.query_params = parse_qs(parse_result.query)

        self.client = client
        self.response = response

    def __getattr__(self, name):
        if self.response:
            return getattr(self.response, name)
        raise AttributeError(name)

    def _compose_url(self, path):
        return url_join(self.url, path)

    def get(self, path='', **kwargs):
        """
        | Performs http GET request through ``self.client.get``.
        | Note that the actually request url would have ``self.url`` as prefix.

        :return: :class:`kloudless.resources.base.Response` or its subclass
        """
        return self.client.get(self._compose_url(path), **kwargs)

    def post(self, path='', data=None, json=None, **kwargs):
        """
        | Performs http POST request through ``self.client.post``.
        | Note that the actually request url would have ``self.url`` as prefix.

        :return: :class:`kloudless.resources.base.Response` or its subclass
        """
        return self.client.post(self._compose_url(path), data, json, **kwargs)

    def put(self, path='', data=None, **kwargs):
        """
        | Performs http PUT request through ``self.client.put``.
        | Note that the actually request url would have ``self.url`` as prefix.

        :return: :class:`kloudless.resources.base.Response` or its subclass
        """
        return self.client.put(self._compose_url(path), data, **kwargs)

    def patch(self, path='', data=None, **kwargs):
        """
        | Performs http PATCH request through ``self.client.patch``.
        | Note that the actually request url would have ``self.url`` as prefix.

        :return: :class:`kloudless.resources.base.Response` or its subclass
        """
        return self.client.patch(self._compose_url(path), data, **kwargs)

    def delete(self, path='', **kwargs):
        """
        | Performs http DELETE request through ``self.client.delete``.
        | Note that the actually request url would have ``self.url`` as prefix.

        :return: :class:`kloudless.resources.base.Response` or its subclass
        """
        return self.client.delete(self._compose_url(path), **kwargs)

    def _get_self(self):
        """
        Performs GET request to self.url.
        """
        if self.response and self.response.request.method == 'GET':
            orig_request = self.response.request
            response = self.get(orig_request.url, headers=orig_request.headers)
        else:
            response = self.get(self.url)
        return response

    def refresh(self):
        """
        Performs GET request through ``self.client.get`` to ``self.url``, then
        refresh ``self``. The original query parameters and headers would be
        reused if original request is http GET request.
        """
        new = self._get_self()
        self.__init__(new.client, new.url, new.response)


class ResponseJson(Response):
    """
    Base Response class for JSON response.

    **Instance attributes**

    :ivar dict data: JSON data
    """
    def __init__(self, data, **kwargs):

        super(ResponseJson, self).__init__(**kwargs)

        self.data = data

    def refresh(self):
        """
        Perform GET request through ``self.client.get`` to ``self.url``, then
        refresh ``self``. The original query parameters and headers would be
        reused if original request is http GET request.
        """
        new = self._get_self()
        self.__init__(client=new.client, data=new.data,
                      url=new.url, response=new.response)


class Resource(ResponseJson):
    """
    Represents a resource object from API response. A resource object contains
    an identifier and endpoint ( `/{resource_type}/{identifier}` ) for
    retrieving its metadata.

    Example resources include: Files and folders in the Storage API,
    calendar events in the Calendar API, and events in Events API.
    """

    def __init__(self, **kwargs):

        super(Resource, self).__init__(**kwargs)

        self.url = self._construct_url(self.data, self.url)

    def __repr__(self):
        return '<{}({} {}): {}>'.format(
            Resource.__name__,
            self.data.get('api', ''),
            self.data.get('type', '').capitalize(),
            self.data
        )

    @staticmethod
    def _construct_url(data, url):

        href = data.get('href')
        if href:
            return href

        if primary_calendar_alias.search(url):
            return url

        object_api = data.get('api', None)
        object_type = data.get('type', None)
        object_id = str(data.get('id', ''))

        if object_api == 'storage' and object_type in ('file', 'folder'):
            account_url = full_account_pattern.match(url).group(0)
            url = '{}/storage/{}s/{}'.format(account_url, object_type,
                                             object_id)
        else:
            if object_id and not url.rstrip('/').endswith(object_id):
                # construct from ResourceList.__init__
                url = url_join(url, object_id)

        return url


class ResourceList(ResponseJson):
    """
    Represents a list of resources from API response. ResourceList itself is also
    an iterable thorough ``self.objects``.

    **Instance attributes**

    :ivar objects: list of :class:`kloudless.resource.base.Resource` instance
    """
    def __init__(self, **kwargs):

        super(ResourceList, self).__init__(**kwargs)

        self.api = self.data.get('api', empty)
        self.type = self.data.get('type', empty)

        self.is_retrieving_events = bool(events_pattern.search(self.url))

        if self.is_retrieving_events:
            self.cursor = self.data.get('cursor', empty)
            # Record latest_cursor while self.get_paging_iterator run out
            self.latest_cursor = None
        else:
            self.page = self.data.get('page', empty)
            self.next_page = self.data.get('next_page', empty)

        self.objects = []
        for object_data in self.data.get('objects', []):
            self.objects.append(
                Resource(data=object_data, url=self.url,
                         client=self.client)
            )

    def __iter__(self):
        return iter(self.objects)

    def _get_query_params_for_pagination(self):

        params = self.query_params.copy()

        if self.is_retrieving_events and 'cursor' in params:
            del params['cursor']
        elif 'page' in params:
            del params['page']

        return params

    def _get_next_page_identifier(self):

        if self.next_page is not empty:
            return self.next_page

        if self.page is not empty and isinstance(self.page, int):
            return self.page + 1

        return None

    def _get_event_next_page(self):

        if self.cursor is empty or str(self.cursor) == '-1' or not self.objects:
            raise exceptions.NoNextPage(cursor=self.cursor)

        params = self._get_query_params_for_pagination()
        params['cursor'] = self.cursor

        response = self.client.get(self.url, params=params,
                                   headers=self.response.request.headers)
        if not response.objects:
            raise exceptions.NoNextPage(cursor=self.cursor)

        return response

    def _get_next_page(self):

        next_page = self._get_next_page_identifier()
        if next_page is None:
            raise exceptions.NoNextPage()

        params = self._get_query_params_for_pagination()
        params['page'] = next_page

        try:
            response = self.client.get(self.url, params=params,
                                       headers=self.response.request.headers)
        except exceptions.NotFoundException:
            raise exceptions.NoNextPage()

        return response

    def get_next_page(self):
        """
        Get the resources of the next page, if any.

        :return: :class:`kloudless.resources.base.ResourceList`
        :raise: :class:`kloudless.exceptions.NoNextPage`
        """
        if self.is_retrieving_events:
            return self._get_event_next_page()
        else:
            return self._get_next_page()

    def get_paging_iterator(self, max_resources=None):
        """
        Generator to iterate thorough all resources under ``self.objects`` and
        all resources in the following page, if any.

        If retrieving events, ``self.latest_cursor`` is available
        after iterating thorough all events without ``max_resources``
        specified.

        :param max_resources: the maximum quantity of resources that would be
            contained in the returned generator

        :return: generator that yield :class:`kloudless.resources.base.Resource`
            instance
        """
        counter = 0
        resource_list = self

        while resource_list:
            for resource in resource_list:
                yield resource
                counter += 1
                if max_resources is not None and counter == max_resources:
                    return
            try:
                resource_list = resource_list.get_next_page()
            except exceptions.NoNextPage as e:
                if self.is_retrieving_events:
                    self.latest_cursor = e.cursor
                break
