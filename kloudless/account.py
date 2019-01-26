from __future__ import unicode_literals

from . import exceptions
from .application import verify_token
from .client import Client
from .util import url_join


class Account(Client):
    """
    Account class that represents one Kloudless account.

    **Instance attributes**

    :ivar str url: Base url which would be used as prefix for all http method
        calls
    """
    def __init__(self, token=None, api_key=None, account_id=None):
        """
        Either ``token`` or ``api_key`` is needed for instantiation.
        ``account_id`` is needed if ``api_key`` is specified.

        :param token: Bearer token
        :param api_key: API key
        :param account_id: Account ID
        """
        if api_key and not account_id:
            raise exceptions.InvalidParameter(
                "An account_id must be provided if you want to use api_key"
                " to create an account instance"
            )

        super(Account, self).__init__(api_key=api_key, token=token)

        self.account_id = account_id or 'me'
        self.url = url_join(self.url, 'accounts/{}'.format(self.account_id))

    def raw(self, raw_method, raw_uri, **kwargs):
        """
        Method for `Pass-Through API <https://developers.kloudless.com/docs/
        latest/core#header-pass-through-api-1>`_

        :param str raw_method: The value stand for ``X-Kloudless-Raw-Method``
            header

        :param raw_uri:  The value stand for ``X-Kloudless-Raw-URI`` header

        :param kwargs:  kwargs passed to :func:`kloudless.client.Client.post`

        :return: :class:`requests.Response`
        """
        headers = kwargs.setdefault('headers', {})
        headers['X-Kloudless-Raw-Method'] = raw_method
        headers['X-Kloudless-Raw-URI'] = raw_uri
        return self.post('raw', get_raw_response=True, **kwargs)


def get_verified_account(app_id, token):
    """
    Verify the ``token`` belongs to an Application with ``app_id`` and return
    an :class:`kloudless.account.Account` instance.

    :param str app_id: Application ID
    :param str token: Account's Bearer token

    :return: :class:`kloudless.account.Account`
    :raise: :class:`kloudless.exceptions.TokenVerificationFailed`
    """
    verify_token(app_id, token)
    account = Account(token=token)
    return account
