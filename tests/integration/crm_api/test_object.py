import unittest
import os

# Add parent dir to path to import utils
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__),
                '..')))
from test_cases import utils


class CRMObject(unittest.TestCase):

    @utils.allow(services=['salesforce', 'dynamics', 'oracle'])
    def setUp(self):
        self.raw_type = 'Account'
        params = {
            'raw_type': self.raw_type
        }
        data = {
            'name': 'Test API Account Name'
        }
        self.obj = self.account.crm_objects.create(params=params, data=data)

    @utils.allow(services=['salesforce', 'dynamics', 'oracle'])
    def tearDown(self):
        self.obj.delete(raw_type=self.raw_type)

    @utils.allow(services=['salesforce', 'dynamics', 'oracle'])
    def test_list_object(self):
        objects = self.account.crm_objects.all(raw_type=self.raw_type)
        # assert properties
        if objects:
            obj = objects[0]
            self.assertEqual(obj.type, self.raw_type)
            self.assertTrue('raw' in obj)

    @utils.allow(services=['salesforce', 'dynamics', 'oracle'])
    def test_read_object(self):
        obj = self.account.crm_objects.retrieve(self.obj.id,
                                                raw_type=self.raw_type)
        # assert properties
        self.assertEqual(obj.id, self.obj.id)
        self.assertTrue('raw' in obj)
        self.assertEqual(obj.id, self.obj.id)

    @utils.allow(services=['salesforce', 'dynamics', 'oracle'])
    def test_update_object(self):
        obj = self.obj
        obj.description = 'test description'
        obj.save(raw_type='Account')
        self.assertEqual('test description', obj.description)


def test_cases():
    return [utils.create_test_case(acc, CRMObject) for acc in utils.accounts]


if __name__ == '__main__':
    suite = utils.create_suite(test_cases())
    unittest.TextTestRunner(verbosity=2).run(suite)
