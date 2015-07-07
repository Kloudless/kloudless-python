import kloudless
import unittest
import utils
import os

API_KEY = os.environ['API_KEY']
kloudless.configure(api_key=API_KEY)

accounts = utils.get_account_for_each_service()

class File(unittest.TestCase):

    def test_create_file(self):
        test_file = utils.create_test_file(self.account)
        self.assertEqual(test_file.account, self.account.id)

if __name__ == '__main__':
    suite = utils.create_suite([utils.create_test_case(acc, File) for acc in accounts])
    unittest.TextTestRunner(verbosity=2).run(suite)
