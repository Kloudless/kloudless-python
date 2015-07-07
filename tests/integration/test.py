from test_cases import *
import unittest
import os
import kloudless
import inspect
import sys

API_KEY = os.environ['API_KEY']
kloudless.configure(api_key=API_KEY)

accounts = utils.get_account_for_each_service()

if __name__ == '__main__':
    test_classes = []
    for m in sys.modules.keys():
      if 'test_cases.test_' in m:
          test_classes.append(inspect.getmembers(sys.modules[m], inspect.isclass)[0][1])
    cases = []
    for cls in test_classes:
        for acc in accounts:
            cases.append(utils.create_test_case(acc, cls))
    suite = utils.create_suite(cases)
    unittest.TextTestRunner(verbosity=2).run(suite)