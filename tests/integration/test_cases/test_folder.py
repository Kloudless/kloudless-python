import unittest
import os
import random

import utils
import sdk

class Folder(unittest.TestCase):

    def setUp(self):
        self.test_folder = utils.create_or_get_test_folder(self.account)
        self.assertTrue(hasattr(self.test_folder, 'id'))
        self.assertEqual(self.test_folder.type, 'folder')

    def _rand(self):
        return 'folder %s' % random.randint(0, 10e10)

    def test_create_folder(self):
        acc = self.account
        folder_name = '%s sub-%s' % (self.test_folder.name, self._rand())

        acc.folders.create(data={
            'parent_id': self.test_folder.id, 'name': folder_name})
        self.assertTrue(utils.is_folder_present(folder_name, self.test_folder))

        new_folder = acc.folders.create(
            data={'parent_id': self.test_folder.id, 'name': folder_name},
            params={'conflict_if_exists': 'false'})
        self.assertEqual(new_folder.name, folder_name)

        with self.assertRaises(sdk.exceptions.KloudlessException) as cm:
            acc.folders.create(
                data={'parent_id': self.test_folder.id, 'name': folder_name},
                params={'conflict_if_exists': 'true'})
        self.assertEqual(cm.exception.status, 409)

    def test_retrieve_folder_metadata(self):
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

        new_folder = acc.folders.create(data={
            'parent_id': test_folder.id, 'name': self._rand()})
        self.assertTrue(utils.is_folder_present(new_folder.name, test_folder))

    def test_rename_folder(self):
        result = None
        folder = self.account.folders.create(data={
            'parent_id': self.test_folder.id, 'name': self._rand()})
        old_folder_parent = folder.parent
        new_folder_name = folder.name + '_renamed'
        folder.name = new_folder_name
        result = folder.save()
        self.assertTrue(result)
        self.assertEqual(folder.name, new_folder_name)
        self.assertEqual(old_folder_parent, folder.parent)

    def test_move_folder(self):
        acc = self.account
        test_folder = self.test_folder
        folder1 = acc.folders.create(data={
            'parent_id': test_folder.id, 'name': self._rand()})
        folder2 = acc.folders.create(data={
            'parent_id': test_folder.id, 'name': self._rand()})
        self.assertTrue(utils.is_folder_present(folder1.name, test_folder))
        self.assertTrue(utils.is_folder_present(folder2.name, test_folder))
        folder2.parent_id = folder1.id
        folder2.save()
        self.assertFalse(utils.is_folder_present(folder2.name, test_folder))

    def test_copy_folder(self):
        acc = self.account
        test_folder = self.test_folder

        folder1 = acc.folders.create(data={
            'parent_id': test_folder.id, 'name': self._rand()})
        self.assertTrue(utils.is_folder_present(folder1.name, test_folder))
        folder2 = acc.folders.create(data={
            'parent_id': folder1.id, 'name': self._rand()})
        self.assertTrue(utils.is_folder_present(folder2.name, folder1))

        copy = folder1.copy_folder(parent_id=test_folder.id, name='%s copy' % folder1.name)
        self.assertTrue(utils.is_folder_present(copy.name, test_folder))
        self.assertTrue(utils.is_folder_present(folder1.name, test_folder))
        self.assertTrue(utils.is_folder_present(folder2.name, copy))

    def test_delete_folder(self):
        acc = self.account
        test_folder = self.test_folder

        # Test deleting an empty folder
        folder1 = acc.folders.create(data={
            'parent_id': test_folder.id, 'name': self._rand()})
        folder1_name = folder1.name # Deletion removes the name.
        self.assertTrue(utils.is_folder_present(folder1_name, test_folder))
        folder1.delete()
        self.assertFalse(utils.is_folder_present(folder1_name, test_folder))

        # Same as above with recursive=True
        folder1 = acc.folders.create(data={
            'parent_id': test_folder.id, 'name': self._rand()})
        folder1_name = folder1.name
        self.assertTrue(utils.is_folder_present(folder1_name, test_folder))
        folder1.delete(recursive=True)
        self.assertFalse(utils.is_folder_present(folder1_name, test_folder))

        # Error case: test deleting a non-empty folder without recursive=True
        folder1 = acc.folders.create(data={
            'parent_id': test_folder.id, 'name': self._rand()})
        folder1_name = folder1.name
        self.assertTrue(utils.is_folder_present(folder1_name, test_folder))
        folder2 = acc.folders.create(data={
            'parent_id': folder1.id, 'name': self._rand()})
        folder2_name = folder2.name
        self.assertTrue(utils.is_folder_present(folder2_name, folder1))
        try:
            folder1.delete()
        except:
            pass
        self.assertTrue(utils.is_folder_present(folder2_name, folder1))

        # Test deleting a non-empty folder with recursive=True
        folder1.delete(recursive=True)
        self.assertFalse(utils.is_folder_present(folder1_name, test_folder))

def test_cases():
    return [utils.create_test_case(acc, Folder) for acc in utils.accounts]

if __name__ == '__main__':
    suite = utils.create_suite(test_cases())
    unittest.TextTestRunner(verbosity=2).run(suite)

