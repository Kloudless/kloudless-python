from __future__ import unicode_literals


class KloudlessException(Exception):
    """
    Base exception class inherited by all exceptions of the library.

    **Instance attributes**

    :ivar str message: Error message
    """
    @property
    def default_message(self):
        raise NotImplementedError

    def __init__(self, message=''):
        message = message or self.default_message
        super(KloudlessException, self).__init__(message)


class InvalidParameter(KloudlessException):
    """
    The parameters are invalid in a function call or class instantiation.
    """
    default_message = "The parameter is not valid."


class TokenVerificationFailed(KloudlessException):

    default_message = "The token does not belong to your application."


class OauthFlowFailed(KloudlessException):

    default_message = "Oauth authorization flow failed."


class NoNextPage(KloudlessException):

    default_message = "There's no next page."

    def __init__(self, cursor=None, *args, **kwargs):
        super(NoNextPage, self).__init__(*args, **kwargs)
        self.cursor = cursor  # cursor for next time event retrieving


class APIException(KloudlessException):
    """
    Base Exception class for API requests.

    **Instance attributes**

    :ivar response: :class:`requests.Response` instance if available
    :ivar int status: ``response.status_code``
    :ivar dict error_data: ``response.json()``
    """
    default_message = "Request failed."

    def __init__(self, response, message=''):

        self.response = response
        self.status = response.status_code
        self.error_data = {}

        message = message or self.default_message
        message += ' Error data: ' + response.text
        try:
            self.error_data = response.json()
        except ValueError:
            pass
        else:
            if 'id' in self.error_data:
                message += '[Request ID: {}] {}'.format(
                    self.error_data['id'], message)

        super(APIException, self).__init__(message)


class AuthorizationException(APIException):
    """
    Exception class for ``401`` status code.
    """
    default_message = (
        "Authorization failed. Please double check that the API Key or Token"
        " being used is correct."
    )


class ForbiddenException(APIException):
    """
    Exception class for ``403`` status code.
    """
    default_message = (
        "Request forbidden. The action is not allowed."
    )


class NotFoundException(APIException):
    """
    Exception class for ``404`` status code.
    """
    default_message = 'Not found. Please make sure the url is correct.'


class RateLimitException(APIException):
    """
    Exception class for ``429`` status code.

    **Instance attributes**

    :ivar float retry_after: Delay seconds until next available requests
    """
    default_message = "Rate limiting encountered. Please try again later."

    def __init__(self, *args, **kwargs):
        super(RateLimitException, self).__init__(*args, **kwargs)
        self.retry_after = None
        if 'Retry-After' in self.response.headers:
            self.retry_after = float(self.response.headers['Retry-After'])


class ServerException(APIException):
    """
    Exception class for ``5xx`` status code.
    """
    default_message = (
        "An unknown error occurred! Please contact support@kloudless.com "
        "with the Request ID for more details."
    )
