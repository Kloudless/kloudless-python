from __future__ import unicode_literals

import re

import requests

from . import exceptions
from .auth import APIKeyAuth, BearerTokenAuth
from .re_patterns import download_file_patterns
from .resources import ResourceList, Resource, Response, ResponseJson
from .util import logger, url_join, construct_kloudless_endpoint
from .version import VERSION

try:
    import simplejson as json
except ImportError:
    import json


def handle_response(response):

    if not response.ok:
        logger.error("Request to '{}' failed: {} - {}".format(
            response.url, response.status_code, response.text))
        if response.status_code == 401:
            raise exceptions.AuthorizationException(response=response)
        elif response.status_code == 403:
            raise exceptions.ForbiddenException(response=response)
        elif response.status_code == 404:
            raise exceptions.NotFoundException(response=response)
        elif response.status_code == 429:
            # TODO: retry mechanism for 429 response
            # Might be able to make use of response.request object
            raise exceptions.RateLimitException(response=response)
        elif response.status_code >= 500:
            raise exceptions.ServerException(response=response)
        else:
            raise exceptions.APIException(response=response)

    logger.debug("Request to '{}' succeeded. Status code: {}".format(
        response.url, response.status_code))
    return response


class Session(requests.Session):
    """
    The Session class helps build Kloudless specific headers.
    """
    def __init__(self):
        super(Session, self).__init__()
        self.headers.update({
            'User-Agent': 'kloudless-python/{}'.format(VERSION),
        })

    @staticmethod
    def _update_kloudless_headers(headers, get_raw_data, raw_headers,
                                  impersonate_user_id):
        if isinstance(get_raw_data, bool):
            headers['X-Kloudless-Raw-Data'] = str(get_raw_data).lower()

        if raw_headers and isinstance(raw_headers, dict):
            headers['X-Kloudless-Raw-Headers'] = json.dumps(
                raw_headers)

        if impersonate_user_id:
            headers['X-Kloudless-As-User'] = str(impersonate_user_id)

    def request(self, method, url, api_version=None, get_raw_data=None,
                raw_headers=None, impersonate_user_id=None, **kwargs):
        """
        Override :func:`requests.Session.request` with additional parameters.

        See `API-wide options <https://developers.kloudless.com/docs/latest/
        core#api-wide-options>`_ for more information about `get_raw_data`,
        `raw_headers` and `impersonate_user_id` parameters.

        :param str method: Http method
        :param str url: Request url

        :param int api_version: API version

        :param bool get_raw_data: Set to ``True`` if the ``raw`` object
            from upstream service is present. This is equal to the
            ``X-Kloudless-Raw-Data`` request header.

        :param dict raw_headers: Headers fowarded to upstream service. This is
            equal to the ``X-Kloudless-Raw-Headers`` request header

        :param str impersonate_user_id: User id to access or modify data for
            individual user accounts. This is equal to the
            ``X-Kloudless-As-User`` request header.

        :param kwargs: kwargs passed to :func:`requests.Session.request`

        :return: :class:`requests.Response`

        :raises: :class:`kloudless.exceptions.APIException` or its subclasses
        """
        if api_version is not None:
            url = re.sub(
                r'(https?://.+?/)v\d', r'\1v{}'.format(api_version), url
            )

        self._update_kloudless_headers(kwargs.setdefault('headers', dict()),
                                       get_raw_data, raw_headers,
                                       impersonate_user_id)
        response = handle_response(
            super(Session, self).request(method, url, **kwargs)
        )
        return response


class Client(Session):
    """
    Base Client class to send all http requests in this library.

    **Instance attributes**

    :ivar str url: Base url that will be used as a prefix for all http method
        calls
    """
    def __init__(self, api_key=None, token=None):
        """
        Either ``api_key`` or ``token`` is needed for instantiation.

        :param api_key: API key
        :param token: Bearer token
        """
        super(Client, self).__init__()

        if token:
            self.token = token
            self.auth = BearerTokenAuth(token)
        elif api_key:
            self.api_key = api_key
            self.auth = APIKeyAuth(api_key)
        else:
            raise exceptions.InvalidParameter(
                "An API Key or Bearer Token must be provided. Please check "
                "api_key and token parameters."
            )

        self.url = construct_kloudless_endpoint()

    def _compose_url(self, path):
        return url_join(self.url, path)

    def _create_response_object(self, response):

        url = response.url

        if ('application/json' not in response.headers.get('content-type', '')
                or not response.content):
            return Response(self, url, response)

        try:
            response_data = response.json()
        except ValueError:
            logger.error("Request to {} failed to decode json: {} - {}".format(
                response.url, response.status_code, response.text))
            raise

        type_ = response_data.get('type')
        if type_ == 'object_list':
            return ResourceList(data=response_data, url=url,
                                client=self, response=response)
        elif 'id' in response_data or 'href' in response_data:
            return Resource(
                data=response_data, url=url, client=self, response=response
            )
        else:
            return ResponseJson(data=response_data, url=url,
                                client=self, response=response)

    def request(self, method, path='', get_raw_response=False, **kwargs):
        """
        | Override :func:`kloudless.client.Session.request`.
        | Note that the actual request url will have ``self.url`` as a prefix.

        :param str method: Http method
        :param str path: Request path
        :param str get_raw_response: Set to ``True`` if the raw
            :class:`requests.Response` instance is in the returned value

        :param kwargs: kwargs passed to :func:`kloudless.client.Session.request`

        :return:
            - :class:`requests.Response` if ``get_raw_response`` is ``True``
            - :class:`kloudless.resources.base.Response` or its subclass otherwise
        """
        url = self._compose_url(path)
        response = super(Client, self).request(method, url, **kwargs)

        if get_raw_response:
            return response

        return self._create_response_object(response)

    def get(self, path='', **kwargs):
        """
        | Http GET request.
        | Note that the actual request url will have ``self.url`` as a
          prefix.

        :param str path: Request path
        :param kwargs: See :func:`kloudless.client.Client.request` for more
            options.

        :return: :class:`kloudless.resources.base.Response` or its subclass
        """
        if download_file_patterns.search(path):
            kwargs.setdefault('stream', True)

        return super(Client, self).get(path, **kwargs)

    def post(self, path='', data=None, json=None, **kwargs):
        """
        | Http POST request.
        | Note that the actual request url will have ``self.url`` as a
          prefix.

        :param str path: Request path
        :param data: passed to :func:`request.Request.post`
        :param json: passed to :func:`request.Request.post`
        :param kwargs: See :func:`kloudless.client.Client.request` for more
            options.

        :return: :class:`kloudless.resources.base.Response` or its subclass
        """
        return super(Client, self).post(path, data, json, **kwargs)

    def put(self, path='', data=None, **kwargs):
        """
        | Http PUT request.
        | Note that the actual request url will have ``self.url`` as a
          prefix.

        :param str path: Request path
        :param data: passed to :func:`request.Request.put`
        :param kwargs: See :func:`kloudless.client.Client.request` for more
            options.

        :return: :class:`kloudless.resources.base.Response` or its subclass
        """
        return super(Client, self).put(path, data, **kwargs)

    def patch(self, path='', data=None, **kwargs):
        """
        | Http PATCH request.
        | Note that the actual request url will have ``self.url`` as a
          prefix.

        :param str path: Request path
        :param data: passed to :func:`request.Request.patch`
        :param kwargs: See :func:`kloudless.client.Client.request` for more
            options.

        :return: :class:`kloudless.resources.base.Response` or its subclass
        """
        return super(Client, self).patch(path, data, **kwargs)

    def delete(self, path='', **kwargs):
        """
        | Http DELETE request.
        | Note that the actual request url will have ``self.url`` as a
          prefix.

        :param str path: Request path
        :param kwargs: See :func:`kloudless.client.Client.request` for more
            options.

        :return: :class:`kloudless.resources.base.Response` or its subclass
        """
        return super(Client, self).delete(path, **kwargs)
