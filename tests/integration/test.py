import unittest
import os
import kloudless
import inspect
import sys
from test_cases import utils

API_KEY = None
DEV_KEY = None
BASE_URL = 'https://api.kloudless.com'

os.environ.setdefault('REQUESTS_CA_BUNDLE', os.path.join(os.path.abspath(os.path.dirname('.')), 'kloudless.ca.crt'))

if 'API_KEY' in os.environ:
    API_KEY = os.environ['API_KEY']
    from test_cases import *
if 'DEV_KEY' in os.environ and 'BASE_URL' in os.environ:
    DEV_KEY = os.environ['DEV_KEY']
    BASE_URL = os.environ['BASE_URL']
    from management_api import *

kloudless.configure(api_key=API_KEY, dev_key=DEV_KEY, base_url='https://api.kloudless.com')

if __name__ == '__main__':
    test_classes = []
    for m in sys.modules.keys():
      if '.test_' in m:
            for name, cls in inspect.getmembers(sys.modules[m], inspect.isclass):
                if '.test_' in cls.__module__:
                    test_classes.append(cls)
    cases = []
    management_cases = []
    for cls in test_classes:
        if 'management_api.' in cls.__module__:
            management_cases.append(cls)
            continue
        if 'test_cases.' in cls.__module__:
            for acc in utils.get_account_for_each_service():
                cases.append(utils.create_test_case(acc, cls))

    suite = utils.create_suite(cases)
    unittest.TextTestRunner(verbosity=2).run(suite)
    kloudless.configure(base_url=BASE_URL)
    suite = utils.create_suite(management_cases)
    unittest.TextTestRunner(verbosity=2).run(suite)