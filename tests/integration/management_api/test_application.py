import unittest
import os
import random

# Add parent dir to path to import utils
import sys
sys.path.insert(0,
    os.path.abspath(os.path.join(os.path.dirname(__file__),
        '..')))
from test_cases import utils
import sdk

class Application(unittest.TestCase):

    def setUp(self):
        self.app = sdk.Application.create(name='testApp')

    def tearDown(self):
        self.app.delete()

    def test_list_active_applications(self):
        for app in sdk.Application.all(active=True):
            self.assertTrue(app.active)
        self.assertEqual(1, len(sdk.Application.all(page_size=1)))

    def test_create_application(self):
        new_app = None
        try:
            app_name = 'test' + str(random.randint(0, 10**8))
            description = 'random app woo'
            new_app = sdk.Application.create(name=app_name, description=description)
            self.assertEqual(new_app.name, app_name)
            self.assertEqual(new_app.description, description)
            self.assertTrue(new_app.active)
            self.assertTrue(new_app.id in [i.id for i in sdk.Application.all()])
        finally:
            if new_app:
                new_app.delete()

    def test_retrieve_app(self):
        app = sdk.Application.retrieve(id=self.app.id)
        self.assertEqual(app, self.app)

    def test_update_application(self):
        description = 'testytest'
        name = 'more testing'
        self.app.name =  name
        self.app.description = description
        self.app.save()
        app = sdk.Application.retrieve(id=self.app.id)
        self.assertEqual(app.description, description)
        self.assertEqual(app.name, name)

if __name__ == '__main__':
    suite = utils.create_suite([Application])
    unittest.TextTestRunner(verbosity=2).run(suite)
