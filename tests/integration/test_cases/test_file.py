import kloudless
import unittest
import utils
import os
import json
from kloudless.exceptions import KloudlessException as KException

class File(unittest.TestCase):

    # need to perform CRUD on existing file
    def setUp(self):
        self.file = utils.create_test_file(self.account)

    # delete test folder
    def tearDown(self):
        self.tearDownClass()

    # CREATE
    def test_create_file(self):
        self.assertEqual(self.file.account, self.account.id)

    # Read
    def test_read_file(self):
        read_file = self.account.files.retrieve(self.file.id)
        self.assertTrue(hasattr(read_file, 'id'))
        self.assertTrue(hasattr(read_file, 'name'))
        self.assertTrue(hasattr(read_file, 'size'))
        self.assertTrue(hasattr(read_file, 'created'))
        self.assertTrue(hasattr(read_file, 'modified'))
        self.assertEqual(read_file.type, 'file')
        self.assertTrue(hasattr(read_file, 'account'))
        self.assertTrue(hasattr(read_file, 'parent'))
        self.assertTrue(hasattr(read_file, 'ancestors'))
        self.assertTrue(hasattr(read_file, 'path'))
        self.assertTrue(hasattr(read_file, 'mime_type'))
        self.assertTrue(hasattr(read_file, 'downloadable'))

    # Update [rename/move]
    def test_patch_file(self):
        update_file = self.file.save(name='test-rename.txt')
        read_file = self.account.files.retrieve(self.file.id)
        self.assertEqual(self.file.account, self.account.id)

    # Update [update contents]
    def test_put_file(self):
        self.file.update('hello there')
        self.assertTrue(self.file.contents().text == 'hello there')

    # Delete
    def test_delete_file(self):
        try:
            self.file.delete(permanent=True)
            read_file = self.account.files.retrieve(self.file.id)
        except KException, e:
            error_data = json.loads(str(e).split('Error data: ')[1])
            self.assertEqual(error_data['status_code'], 404)

if __name__ == '__main__':
    suite = utils.create_suite([utils.create_test_case(acc, File) for acc in utils.accounts])
    unittest.TextTestRunner(verbosity=2).run(suite)
