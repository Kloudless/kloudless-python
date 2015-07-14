import kloudless
import unittest
import utils
import os

API_KEY = os.environ['API_KEY']
kloudless.configure(api_key=API_KEY)

accounts = utils.get_account_for_each_service()

class Folder(unittest.TestCase):

    def setUp(self):
      self.test_folder = utils.create_or_get_test_folder(self.account)

    def tearDown(self):
      self.tearDownClass()

    def test_create_folder(self):
      acc = self.account
      folder_name = 'test_create_folder'
      test_folder = self.test_folder
      self.assertTrue(hasattr(test_folder, 'id'))
      self.assertEqual(test_folder.type, 'folder')

      acc.folders.create(parent_id=test_folder.id, name=folder_name)
      self.assertTrue(utils.is_folder_present(folder_name, test_folder))

    def test_retrieve_folder_metadata(self):
      acc = self.account
      test_folder = self.test_folder
      self.assertTrue(hasattr(test_folder, 'account'))
      self.assertTrue(hasattr(test_folder, 'can_create_folders'))
      self.assertTrue(hasattr(test_folder, 'can_upload_files'))
      self.assertTrue(hasattr(test_folder, 'id'))
      self.assertTrue(hasattr(test_folder, 'name'))
      self.assertTrue(hasattr(test_folder, 'parent'))
      self.assertTrue(hasattr(test_folder, 'path'))
      self.assertTrue(hasattr(test_folder, 'type'))

    def test_retrieve_folder_contents(self):
      acc = self.account
      test_folder = self.test_folder
      contents = test_folder.contents()
      self.assertTrue(hasattr(contents, 'count'))
      self.assertTrue(hasattr(contents, 'page'))
      self.assertTrue(hasattr(contents, 'next_page'))

      acc.folders.create(parent_id=test_folder.id, name='folder1')
      contents = test_folder.contents()
      self.assertTrue(len(contents) == 1)

    def test_rename_folder(self):
        result = None
        acc = self.account
        folder = self.test_folder
        new_folder_name = folder.name + '_renamed'
        folder_contents = folder.contents()
        folder.name = new_folder_name
        result = folder.save()
        self.assertTrue(result)
        self.assertEqual(folder.name, new_folder_name)
        self.assertEqual(folder.contents(), folder_contents)

    def test_move_folder(self):
      acc = self.account
      test_folder = self.test_folder
      folder1 = acc.folders.create(parent_id=test_folder.id, name='folder1')
      folder2 = acc.folders.create(parent_id=test_folder.id, name='folder2')
      self.assertTrue(utils.is_folder_present('folder1', test_folder))
      self.assertTrue(utils.is_folder_present('folder2', test_folder))
      folder2.parent_id = folder1.id
      folder2.save()
      self.assertFalse(utils.is_folder_present('folder2', test_folder))

    def test_copy_folder(self):
      acc = self.account
      test_folder = self.test_folder

      folder1 = acc.folders.create(parent_id=test_folder.id, name='folder1')
      self.assertTrue(utils.is_folder_present('folder1', test_folder))
      acc.folders.create(parent_id=folder1.id, name='folder2')
      self.assertTrue(utils.is_folder_present('folder2', folder1))

      copy = folder1.copy_folder(parent_id=test_folder.id, name='folder1_copy')
      self.assertTrue(utils.is_folder_present('folder1_copy', test_folder))
      self.assertTrue(utils.is_folder_present('folder1', test_folder))
      self.assertTrue(utils.is_folder_present('folder2', copy))

    def test_delete_folder(self):
      acc = self.account
      test_folder = self.test_folder

      # Test deleting an empty folder
      folder1 = acc.folders.create(parent_id=test_folder.id, name='folder1')
      self.assertTrue(utils.is_folder_present('folder1', test_folder))
      folder1.delete()
      self.assertFalse(utils.is_folder_present('folder1', test_folder))

      # Same as above with recursive=True
      folder1 = acc.folders.create(parent_id=test_folder.id, name='folder1')
      self.assertTrue(utils.is_folder_present('folder1', test_folder))
      folder1.delete(recursive=True)
      self.assertFalse(utils.is_folder_present('folder1', test_folder))

      # Error case: test deleting a non-empty folder without recursive=True
      folder1 = acc.folders.create(parent_id=test_folder.id, name='folder1')
      self.assertTrue(utils.is_folder_present('folder1', test_folder))
      folder2 = acc.folders.create(parent_id=folder1.id, name='folder2')
      self.assertTrue(utils.is_folder_present('folder2', folder1))
      try:
        folder1.delete()
      except:
        pass
      self.assertTrue(utils.is_folder_present('folder2', folder1))

      # Test deleting a non-empty folder with recursive=True
      folder1.delete(recursive=True)
      self.assertFalse(utils.is_folder_present('folder1', test_folder))

if __name__ == '__main__':
    suite = utils.create_suite([utils.create_test_case(acc, Folder) for acc in accounts])
    unittest.TextTestRunner(verbosity=2).run(suite)

