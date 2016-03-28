import unittest
import os
import datetime

# Add parent dir to path to import utils
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__),
                '..')))
from test_cases import utils
import sdk


class CRMOpportunity(unittest.TestCase):

    def setUp(self):
        account_id = 832496
        self.account = sdk.Account.retrieve(id=account_id)
        data = {
            'name': 'API Test Opportunity Name',
            'stage_name': 'open',
            'close_date': datetime.datetime.today().strftime(
                "%Y-%m-%dT%H:%M:%SZ")
        }
        self.obj = self.account.crm_opportunities.create(data=data)

    def tearDown(self):
        self.obj.delete()

    def test_list_object(self):
        objects = self.account.crm_opportunities.all()
        # assert properties
        if objects:
            obj = objects[0]
            self.assertEqual(obj.type, 'Opportunity')
            self.assertTrue('raw' in obj)

    def test_read_object(self):
        obj = self.account.crm_opportunities.retrieve(self.obj.id)
        # assert Opportunity properties
        self.assertEqual(obj.id, self.obj.id)
        self.assertEqual(obj.type, 'Opportunity')
        self.assertTrue('raw' in obj)

        self.assertTrue('created' in obj)
        self.assertTrue('modified' in obj)
        self.assertTrue('description' in obj)

    def test_update_object(self):
        obj = self.obj
        obj.description = 'test opportunity description'
        obj.save()
        self.assertEqual('test opportunity description', obj.description)


def test_cases():
    return [CRMOpportunity]

if __name__ == '__main__':
    suite = utils.create_suite(test_cases())
    unittest.TextTestRunner(verbosity=2).run(suite)
