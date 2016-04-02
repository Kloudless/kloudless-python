import unittest
import os

import utils
import sdk

class Keys(unittest.TestCase):

    keys = None

    def setUp(self):
        self.keys = self.account.keys.all()
        
    def test_list_keys(self):
        if self.keys:
            for key in self.keys:
                self.assertIsInstance(key, sdk.resources.Key)

    def test_retrieve_key(self):
        if not self.keys:
            return
        key = self.account.keys.retrieve(self.keys[0].id)
        self.assertIsInstance(key, sdk.resources.Key)
        self.assertEquals(self.keys[0].id, key.id)

def test_cases():
    return [utils.create_test_case(acc, Keys) for acc in utils.accounts]

if __name__ == '__main__':
    suite = utils.create_suite(test_cases())
    unittest.TextTestRunner(verbosity=2).run(suite)
