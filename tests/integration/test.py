import unittest
import os
import inspect
import sys

from test_cases import *
from management_api import *

os.environ.setdefault('REQUESTS_CA_BUNDLE', os.path.join(os.path.abspath(os.path.dirname('..')), 'kloudless.ca.crt'))

def test_cases():
    test_classes = []
    for m in sys.modules.keys():
      if '.test_' in m:
            for name, cls in inspect.getmembers(sys.modules[m], inspect.isclass):
                if '.test_' in cls.__module__:
                    test_classes.append(cls)

    cases = []
    for cls in test_classes:
        if utils.DEV_KEY:
            if 'management_api.' in cls.__module__:
                cases.append(cls)
                continue
        if utils.API_KEY:
            if 'test_cases.' in cls.__module__:
                for acc in utils.accounts:
                    cases.append(utils.create_test_case(acc, cls))

    return cases

if __name__ == '__main__':
    suite = utils.create_suite(test_cases())
    unittest.TextTestRunner(verbosity=2).run(suite)
