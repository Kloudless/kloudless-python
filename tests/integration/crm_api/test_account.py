import unittest
import os

# Add parent dir to path to import utils
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__),
                '..')))
from test_cases import utils


class CRMAccount(unittest.TestCase):

    @utils.allow(services=['salesforce', 'dynamics', 'oracle'])
    def setUp(self):
        data = {
            'name': 'Test API Account Name'
        }
        self.obj = self.account.crm_accounts.create(data=data)

    @utils.allow(services=['salesforce', 'dynamics', 'oracle'])
    def tearDown(self):
        self.obj.delete()

    @utils.allow(services=['salesforce', 'dynamics', 'oracle'])
    def test_list_object(self):
        objects = self.account.crm_accounts.all()
        # assert properties
        if objects:
            obj = objects[0]
            self.assertEqual(obj.type, 'Account')
            self.assertTrue('raw' in obj)

    @utils.allow(services=['salesforce', 'dynamics', 'oracle'])
    def test_read_object(self):
        obj = self.account.crm_accounts.retrieve(self.obj.id)
        # assert Account properties
        self.assertEqual(obj.id, self.obj.id)
        self.assertEqual(obj.type, 'Account')
        self.assertTrue('raw' in obj)

        # Account specific properties
        self.assertTrue('id' in obj)
        self.assertTrue('name' in obj)
        self.assertTrue('industry_code' in obj)
        self.assertTrue('industry' in obj)
        self.assertTrue('employees' in obj)
        self.assertTrue('rating' in obj)
        self.assertTrue('fax' in obj)
        self.assertTrue('phone' in obj)
        self.assertTrue('website' in obj)
        self.assertTrue('annual_revenue' in obj)
        self.assertTrue('website' in obj)

        self.assertTrue('created' in obj)
        self.assertTrue('modified' in obj)
        self.assertTrue('description' in obj)

    @utils.allow(services=['salesforce', 'dynamics', 'oracle'])
    def test_update_object(self):
        obj = self.obj
        obj.description = 'test account description'
        obj.save()
        self.assertEqual('test account description', obj.description)


def test_cases():
    return [utils.create_test_case(acc, CRMAccount) for acc in utils.accounts]

if __name__ == '__main__':
    suite = utils.create_suite(test_cases())
    unittest.TextTestRunner(verbosity=2).run(suite)
