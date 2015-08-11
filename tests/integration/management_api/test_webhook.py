import kloudless
import unittest
import os
import time

# Add parent dir to path to import utils
import sys
sys.path.insert(0,
    os.path.abspath(os.path.join(os.path.dirname(__file__),
        '..')))
from test_cases import utils

class WebHook(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = kloudless.Application.create(name='testApp')
        cls.app.apikeys.create()
        cls.app_id = cls.app.id
        cls.url = "https://kloudless-webhooks-receiver.herokuapp.com?app_id=%s" % cls.app_id
        cls.app.webhooks.create(url=cls.url)

    @classmethod
    def tearDownClass(cls):
        cls.app.delete()

    @utils.order
    def test_create_webhook(self):
        webhook = self.app.webhooks.create(url=self.url)
        webhooks = self.app.webhooks.all()
        self.assertTrue(webhook.id in [w.id for w in webhooks])

    @utils.order
    def test_list_webhooks(self):
        self.assertEqual(len(self.app.webhooks.all()), 2)

    @utils.order
    def test_retrieve_webhook(self):
        webhook = self.app.webhooks.create(url=self.url)
        retrieved_webhook = self.app.webhooks.retrieve(id=webhook.id)
        self.assertEqual(webhook, retrieved_webhook)

    @utils.order
    def test_list_page_size(self):
        webhooks = self.app.webhooks.all(page_size=1)
        self.assertEqual(len(webhooks), 1)
        self.assertEqual(len(self.app.webhooks.all()), 3)

    @utils.order
    def test_delete_webhook(self):
        for webhook in self.app.webhooks.all():
            webhook.delete()
        webhooks = self.app.webhooks.all()
        self.assertEqual(len(webhooks), 0)

if __name__ == '__main__':
    suite = utils.create_suite([WebHook])
    unittest.TextTestRunner(verbosity=2).run(suite)