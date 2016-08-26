from .version import VERSION
__version__ = VERSION

from .config import configure
from .resources import (BaseResource, Account, File, Folder, Link,
                        Application)
