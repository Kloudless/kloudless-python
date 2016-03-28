import unittest
import os

# Add parent dir to path to import utils
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__),
                '..')))
from test_cases import utils
import sdk


class CRMEvents(unittest.TestCase):

    def setUp(self):
        account_id = 832496
        self.account = sdk.Account.retrieve(id=account_id)

    def test_events(self):
        objects = self.account.crm_events.all()
        if objects:
            obj = objects[0]
            self.assertTrue('type' in obj)

        self.assertTrue(objects)


def test_cases():
    return [CRMEvents]

if __name__ == '__main__':
    suite = utils.create_suite(test_cases())
    unittest.TextTestRunner(verbosity=2).run(suite)
