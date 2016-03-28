import unittest
import os

# Add parent dir to path to import utils
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__),
                '..')))
from test_cases import utils
import sdk


class CRMSearch(unittest.TestCase):

    def setUp(self):
        account_id = 832496
        self.account = sdk.Account.retrieve(id=account_id)

    def test_search(self):
        query = ''
        lang = ''
        if self.account.service == 'salesforce':
            query = 'SELECT Id from Account'
            lang = 'SOQL'
        else:
            query = 'test'
            lang = 'KEYWORD'

        objects = self.account.crm_search.all(q=query, lang=lang)
        if objects:
            obj = objects[0]
            self.assertTrue('type' in obj)
            self.assertTrue('raw' in obj)

        self.assertTrue(objects)


def test_cases():
    return [CRMSearch]

if __name__ == '__main__':
    suite = utils.create_suite(test_cases())
    unittest.TextTestRunner(verbosity=2).run(suite)
