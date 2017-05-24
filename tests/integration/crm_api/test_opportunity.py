import unittest
import os
import datetime

# Add parent dir to path to import utils
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__),
                '..')))
from test_cases import utils


class CRMOpportunity(unittest.TestCase):

    @utils.allow(apis=['crm'])
    def setUp(self):
        data = {
            'name': 'API Test Opportunity Name',
            'stage_name': 'open',
            'close_date': datetime.datetime.today().strftime(
                "%Y-%m-%dT%H:%M:%SZ")
        }
        self.obj = self.account.crm_opportunities.create(data=data)

    @utils.allow(apis=['crm'])
    def tearDown(self):
        self.obj.delete()

    @utils.allow(apis=['crm'], capabilities=['can_crud_crm_opportunities'])
    def test_list_object(self):
        objects = self.account.crm_opportunities.all()
        # assert properties
        if objects:
            obj = objects[0]
            self.assertEqual(obj.type, 'opportunity')
            self.assertTrue('raw' in obj)

    @utils.allow(apis=['crm'], capabilities=['can_crud_crm_opportunities'])
    def test_read_object(self):
        obj = self.account.crm_opportunities.retrieve(self.obj.id)
        # assert Opportunity properties
        self.assertEqual(obj.id, self.obj.id)
        self.assertEqual(obj.type, 'opportunity')
        self.assertTrue('raw' in obj)

        self.assertTrue('created' in obj)
        self.assertTrue('modified' in obj)
        self.assertTrue('description' in obj)

    @utils.allow(apis=['crm'], capabilities=['can_crud_crm_opportunities'])
    def test_update_object(self):
        obj = self.obj
        obj.description = 'test opportunity description'
        obj.save()
        self.assertEqual('test opportunity description', obj.description)


def test_cases():
    return [utils.create_test_case(acc,
                                   CRMOpportunity) for acc in utils.accounts]

if __name__ == '__main__':
    suite = utils.create_suite(test_cases())
    unittest.TextTestRunner(verbosity=2).run(suite)
