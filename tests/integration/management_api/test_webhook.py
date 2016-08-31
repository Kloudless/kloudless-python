import unittest
import os
import base64
import time

# Add parent dir to path to import utils
import sys
sys.path.insert(0,
    os.path.abspath(os.path.join(os.path.dirname(__file__),
        '..')))
from test_cases import utils
import sdk

class WebHook(unittest.TestCase):

    def setUp(self):
        name = base64.b64encode(os.urandom(12))
        self.app = sdk.Application.create(data={'name': name})
        self.app.apikeys.create()
        self.url = "https://kloudless-webhooks-receiver.herokuapp.com?app_id=%s" % self.app.id
        self.webhook = self.app.webhooks.create(data={'url': self.url})

    def tearDown(self):
        self.app.delete()

    def test_create_webhook(self):
        webhooks = self.app.webhooks.all()
        self.assertTrue(self.webhook.id in [w.id for w in webhooks])

    def test_list_webhooks(self):
        self.app.webhooks.create(data={'url': self.url})
        self.assertEqual(len(self.app.webhooks.all()), 2)

    def test_retrieve_webhook(self):
        retrieved_webhook = self.app.webhooks.retrieve(id=self.webhook.id)
        self.assertEqual(self.webhook, retrieved_webhook)

    def test_list_page_size(self):
        self.app.webhooks.create(data={'url': self.url})
        webhooks = self.app.webhooks.all(page_size=1)
        self.assertEqual(len(webhooks), 1)
        self.assertEqual(len(self.app.webhooks.all()), 2)

    def test_delete_webhook(self):
        for webhook in self.app.webhooks.all():
            webhook.delete()
        webhooks = self.app.webhooks.all()
        self.assertEqual(len(webhooks), 0)

def test_cases():
    return [WebHook]

if __name__ == '__main__':
    suite = utils.create_suite(test_cases())
    unittest.TextTestRunner(verbosity=2).run(suite)
