import unittest
import random
import time

import utils
import sdk
import helpers


class File(unittest.TestCase):

    # need to perform CRUD on existing file
    @utils.allow(apis=['storage'])
    def setUp(self):
        self.folder = utils.create_or_get_test_folder(self.account)
        self.file = utils.create_test_file(self.account)

    # CREATE
    @utils.allow(apis=['storage'], capabilities=['can_upload_file'])
    def test_create_file(self):
        self.assertEqual(self.file.account, self.account.id)
        new_file = utils.create_test_file(self.account, file_data='test data1',
                                          overwrite=False)
        self.assertNotEqual(self.file.name, new_file.name)
        new_file = utils.create_test_file(
            self.account, file_data='test data2', file_name=self.file.name,
            overwrite=True)
        self.assertEqual(self.file.name, new_file.name)

    # Read
    @utils.allow(apis=['storage'])
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

    # Rename, Move and Copy
    @utils.allow(apis=['storage'], capabilities=['can_rename_file'])
    def test_rename_file(self):
        new_name = 'renamed %s' % self.file.name
        self.file.name = new_name
        self.assertTrue(self.file.save())
        self.assertEqual(self.file.name, new_name)
        self.assertEqual(self.file.account, self.account.id)

    @utils.allow(apis=['storage'], capabilities=['can_move_file'])
    def test_move_file(self):
        new_name = 'moved %s' % self.file.name
        folder1 = self.account.folders.create(
            data={'parent_id': self.folder.id,
                  'name': 'folder %s' % random.randint(0, 10e10)})
        self.assertTrue(utils.is_folder_present(folder1.name, self.folder))
        self.file.parent_id = folder1.id
        self.file.name = new_name
        self.assertTrue(self.file.name, new_name)
        self.assertTrue(self.file.save())
        self.assertFalse(utils.is_file_present(self.file.name, self.folder))
        self.assertTrue(utils.is_file_present(self.file.name, folder1))

    @utils.allow(apis=['storage'], capabilities=['can_copy_file'])
    def test_copy_file(self):
        new_name = 'copied %s' % self.file.name
        folder1 = self.account.folders.create(
            data={'parent_id': self.folder.id,
                  'name': 'folder %s' % random.randint(0, 10e10)})
        self.assertTrue(utils.is_folder_present(folder1.name, self.folder))
        new_file = self.file.copy_file(parent_id=folder1.id, name=new_name)
        self.assertTrue(new_file)
        self.assertTrue(new_file.name, new_name)
        self.assertTrue(utils.is_file_present(self.file.name, self.folder))
        self.assertTrue(utils.is_file_present(new_file.name, folder1))

    # Update [update contents]
    @utils.allow(apis=['storage'], capabilities=['can_update_file_content'])
    def test_put_file(self):
        expected_file_contents = u'h\xe9llo there'.encode('utf8')
        self.file.update(file_data=expected_file_contents)
        file_contents = self.file.contents().content
        self.assertTrue(file_contents == expected_file_contents)

    # Delete
    @utils.allow(apis=['storage'], capabilities=['can_delete_file'])
    def test_delete_file(self):
        try:
            self.file.delete()
            self.account.files.retrieve(self.file.id)
        except sdk.exceptions.KloudlessException, e:
            self.assertEqual(e.status, 404)

    # Delete Permanent
    @utils.allow(apis=['storage'],
                 capabilities=['can_delete_file_permanently'])
    def test_delete_file_permanent(self):
        try:
            self.file.delete(permanent=True)
            self.account.files.retrieve(self.file.id)
        except sdk.exceptions.KloudlessException, e:
            self.assertEqual(e.status, 404)

    @utils.allow(services=['gdrive', 'dropbox', 'box'], apis=['storage'],
                 capabilities=['permissions_supported_for_files'])
    def test_permissions(self):
        helpers.permission_testing(self, self.file)

    @utils.allow(services=['gdrive', 'box'], apis=['storage'],
                 capabilities=['can_list_properties'])
    def test_list_properties(self):
        # GET Properties of File
        properties = self.file.properties.all()

        # Assertion
        self.assertEqual(len(properties), 0)

    @utils.allow(services=['gdrive', 'box'], apis=['storage'],
                 capabilities=['properties_supported_for_files'])
    def test_update_properties(self):
        # ADD Properties of File
        properties = [
            {'key': 'key1', 'value': 'value1'},
            {'key': 'key2', 'value': 'value2'}
        ]
        properties = self.file.properties.update(data=properties)
        time.sleep(0.5)

        # Assertion
        self.assertEqual(len(properties['properties']), 2)
        for prop in properties['properties']:
            self.assertIn(prop["key"], ["key1", "key2"])
            self.assertIn(prop["value"], ["value1", "value2"])

        # Update and Delete Properties of File
        properties = [
            {'key': 'key1', 'value': None},  # delete property
            {'key': 'key2', 'value': 'hello'},  # update property
            {'key': 'key3', 'value': 'value3'}  # add property
        ]
        properties = self.file.properties.update(data=properties)
        time.sleep(0.5)

        # Assertion
        self.assertEqual(len(properties['properties']), 2)
        for prop in properties['properties']:
            self.assertIn(prop["key"], ["key3", "key2"])
            self.assertIn(prop["value"], ["value3", "hello"])

    @utils.allow(services=['gdrive', 'box'], apis=['storage'],
                 capabilities=['can_delete_all_properties'])
    def test_delete_all_properties(self):
        # Delete All Properties of File
        delete_all = self.file.properties.delete_all()

        # Assertion
        self.assertTrue(delete_all)

    @utils.allow(services=['s3'], apis=['storage'])
    def test_upload_url(self):
        contents = self.account.folders().contents()
        name = 'test_file_name'
        if contents:
            obj = contents[0]
            data = {}
            data['parent_id'] = obj.id
            data['name'] = name
            response = self.account.files.upload_url(data=data)
            self.assertTrue('url' in response)


def test_cases():
    return [utils.create_test_case(acc, File) for acc in utils.accounts]


if __name__ == '__main__':
    suite = utils.create_suite(test_cases())
    unittest.TextTestRunner(verbosity=2).run(suite)
