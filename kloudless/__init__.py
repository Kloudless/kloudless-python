from .account import Account, get_verified_account
from .application import (get_authorization_url, get_token_from_code,
                          verify_token)
from .client import Client
from .config import configuration
from .version import VERSION

__version__ = VERSION
