import kloudless
import unittest
import os
import utils

API_KEY = os.environ['API_KEY']
kloudless.configure(api_key=API_KEY)

accounts = utils.get_account_for_each_service()

class Recent(unittest.TestCase):
    pass

if __name__ == '__main__':
    suite = utils.create_suite([utils.create_test_case(acc, Recent) for acc in accounts])
    unittest.TextTestRunner(verbosity=2).run(suite)
