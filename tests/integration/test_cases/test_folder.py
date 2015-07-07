import kloudless
import unittest
import utils
import os

API_KEY = os.environ['API_KEY']
kloudless.configure(api_key=API_KEY)

accounts = utils.get_account_for_each_service()

class Folder(unittest.TestCase):

    def test_rename_folder(self):
        new_folder_name = 'testFolder2'
        result = None
        acc = self.account
        folder = utils.create_or_get_test_folder(acc)
        folder_contents = folder.contents()
        folder.name = new_folder_name
        result = folder.save()
        self.assertTrue(result)
        self.assertEqual(folder.name, new_folder_name)
        self.assertEqual(folder.contents(), folder_contents)


if __name__ == '__main__':
    suite = utils.create_suite([utils.create_test_case(acc, Folder) for acc in accounts])
    unittest.TextTestRunner(verbosity=2).run(suite)

