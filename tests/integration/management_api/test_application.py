import kloudless
import unittest
import os

DEV_KEY = os.environ.get('DEV_KEY')
BASE_URL = os.environ.get('BASE_URL')

kloudless.configure(dev_key=DEV_KEY, base_url=BASE_URL)

class Application(unittest.TestCase):

    def test_list_active_applications(self):
        for app in kloudless.Application.all(active=True):
            self.assertTrue(app.active)

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(Application)
    unittest.TextTestRunner(verbosity=2).run(suite)