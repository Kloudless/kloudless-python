import kloudless
import unittest
import os

# Add parent dir to path to import utils
import sys
sys.path.insert(0,
    os.path.abspath(os.path.join(os.path.dirname(__file__),
        '..')))
from test_cases import utils

class APIKey(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = kloudless.Application.create(name='test')

    @classmethod
    def tearDownClass(cls):
        cls.app.delete()

    @utils.order
    def test_create_api_key(self):
        key = self.app.apikeys.create()
        keys = self.app.apikeys.all()
        self.assertTrue(key.key in [k.key for k in keys])


    @utils.order
    def test_list_page_size(self):
        key = self.app.apikeys.create()
        keys = self.app.apikeys.all(page_size=1)
        self.assertEqual(len(keys), 1)
        self.assertEqual(len(self.app.apikeys.all()), 2)

    @utils.order
    def test_delete_key(self):
        for i in range(1):
            for key in self.app.apikeys.all(page=i):
                key.delete()
        keys = self.app.apikeys.all()
        self.assertEqual(len(keys), 0)

if __name__ == '__main__':
    suite = utils.create_suite([APIKey])
    unittest.TextTestRunner(verbosity=2).run(suite)
