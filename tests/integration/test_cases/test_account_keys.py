import kloudless
import unittest
import os
import utils

class Keys(unittest.TestCase):

    keys = None

    def setUp(self):
        self.keys = self.account.keys.all()
        
    def test_list_keys(self):
        if self.keys:
            for key in self.keys:
                self.assertIsInstance(key, kloudless.resources.Key)

    def test_retrieve_key(self):
        if not self.keys:
            return
        key = self.account.keys.retrieve(self.keys[0].id)
        self.assertIsInstance(key, kloudless.resources.Key)
        self.assertEquals(self.keys[0].id, key.id)

if __name__ == '__main__':
    suite = utils.create_suite([utils.create_test_case(acc, Keys) for acc in utils.accounts])
    unittest.TextTestRunner(verbosity=2).run(suite)
