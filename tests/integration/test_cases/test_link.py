import kloudless
import unittest
import os
import utils
import requests

API_KEY = os.environ['API_KEY']
kloudless.configure(api_key=API_KEY)

accounts = utils.get_account_for_each_service()

class Link(unittest.TestCase):

    def test_create_link(self):
        test_file = utils.create_test_file(self.account)
        link = self.account.links.create(file_id=test_file.id)
        self.assertEqual(link.file_id, test_file.id)

    def test_create_direct_link(self):
        test_file = utils.create_test_file(self.account)
        link = self.account.links.create(file_id=test_file.id, direct=True)
        r = requests.get(link.url)
        self.assertEqual(r.text, 'test')


if __name__ == '__main__':
    suite = utils.create_suite([utils.create_test_case(acc, Link) for acc in accounts])
    unittest.TextTestRunner(verbosity=2).run(suite)
