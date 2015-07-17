import kloudless
import unittest
import os

DEV_KEY = os.environ.get('DEV_KEY')
BASE_URL = os.environ.get('BASE_URL')

kloudless.configure(dev_key=DEV_KEY, base_url=BASE_URL)

class APIKey(unittest.TestCase):

    def test_list_page_size(self):
        app = kloudless.Application.all()[0]
        keys = app.apikeys.all(page_size=1)
        self.assertEqual(len(keys), 1)

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(APIKey)
    unittest.TextTestRunner(verbosity=2).run(suite)