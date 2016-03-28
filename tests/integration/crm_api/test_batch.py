import unittest
import os

# Add parent dir to path to import utils
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__),
                '..')))
from test_cases import utils
import sdk


class CRMBatch(unittest.TestCase):

    def setUp(self):
        account_id = 832496
        self.account = sdk.Account.retrieve(id=account_id)

    def test_batch(self):
        data = {
            'requests': [{
                'id': '12345',
                'method': 'GET',
                'url_data': {
                    'raw_type': 'Account'
                }
            }]
        }
        response = self.account.crm_batch.create(data=data)
        self.assertTrue(response['responses'] or response['errors'])


def test_cases():
    return [CRMBatch]

if __name__ == '__main__':
    suite = utils.create_suite(test_cases())
    unittest.TextTestRunner(verbosity=2).run(suite)
