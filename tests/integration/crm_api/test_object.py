import unittest
import os

# Add parent dir to path to import utils
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__),
                '..')))
from test_cases import utils
import sdk


class CRMObject(unittest.TestCase):

    def setUp(self):
        account_id = 832496
        self.raw_type = 'Account'
        self.account = sdk.Account.retrieve(id=account_id)
        params = {
            'raw_type': self.raw_type
        }
        data = {
            'name': 'Test API Account Name'
        }
        self.obj = self.account.crm_objects.create(params=params, data=data)

    def tearDown(self):
        self.obj.delete(raw_type=self.raw_type)

    def test_list_object(self):
        self.raw_type = 'Account'
        objects = self.account.crm_objects.all(raw_type=self.raw_type)
        # assert properties
        if objects:
            obj = objects[0]
            self.assertEqual(obj.type, self.raw_type)
            self.assertTrue('raw' in obj)

    def test_read_object(self):
        self.raw_type = 'Account'
        obj = self.account.crm_objects.retrieve(self.obj.id,
                                                raw_type=self.raw_type)
        # assert properties
        self.assertEqual(obj.id, self.obj.id)
        self.assertTrue('raw' in obj)
        self.assertEqual(obj.id, self.obj.id)

    def test_update_object(self):
        self.raw_type = 'Account'
        obj = self.obj
        obj.description = 'test description'
        obj.save(raw_type='Account')
        self.assertEqual('test description', obj.description)


def test_cases():
    return [CRMObject]


if __name__ == '__main__':
    suite = utils.create_suite(test_cases())
    unittest.TextTestRunner(verbosity=2).run(suite)
