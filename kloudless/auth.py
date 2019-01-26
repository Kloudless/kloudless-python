from __future__ import unicode_literals

from requests import auth


class BaseAuth(auth.AuthBase):

    def __init__(self, key):
        self.key = key

    @property
    def scheme(self):
        raise NotImplementedError

    @property
    def auth_header(self):
        return '{} {}'.format(self.scheme, self.key)

    def __call__(self, request):
        request.headers['Authorization'] = self.auth_header
        return request


class APIKeyAuth(BaseAuth):

    scheme = 'APIKey'


class BearerTokenAuth(BaseAuth):

    scheme = 'Bearer'
