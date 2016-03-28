import unittest
import os
import base64

# Add parent dir to path to import utils
import sys
sys.path.insert(0,
    os.path.abspath(os.path.join(os.path.dirname(__file__),
        '..')))
from test_cases import utils
import sdk

class APIKey(unittest.TestCase):

    def setUp(self):
        name = base64.b64encode(os.urandom(12))
        self.app = sdk.Application.create(name="app %s" % name)

    def tearDown(self):
        self.app.delete()

    def test_create_api_key(self):
        key = self.app.apikeys.create()
        keys = self.app.apikeys.all()
        self.assertTrue(key.key in [k.key for k in keys])

    def test_list_page_size(self):
        key1 = self.app.apikeys.create()
        key2 = self.app.apikeys.create()
        keys = self.app.apikeys.all(page_size=1)
        self.assertEqual(len(keys), 1)
        # Including the default API Key created.
        self.assertEqual(len(self.app.apikeys.all()), 3)

    def test_delete_key(self):
        self.app.apikeys.create()
        for key in self.app.apikeys.all():
            key.delete()
        keys = self.app.apikeys.all()
        self.assertEqual(len(keys), 0)

def test_cases():
    return [APIKey]

if __name__ == '__main__':
    suite = utils.create_suite(test_cases())
    unittest.TextTestRunner(verbosity=2).run(suite)
