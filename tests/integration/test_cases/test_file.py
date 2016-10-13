import unittest
import os
import random
import json
import time

import utils
import sdk

class File(unittest.TestCase):

    # need to perform CRUD on existing file
    def setUp(self):
        self.folder = utils.create_or_get_test_folder(self.account)
        self.file = utils.create_test_file(self.account)

    # CREATE
    def test_create_file(self):
        self.assertEqual(self.file.account, self.account.id)
        new_file = utils.create_test_file(self.account, file_data='test data1',
                                          overwrite=False)
        self.assertNotEqual(self.file.name, new_file.name)
        new_file = utils.create_test_file(self.account, file_data='test data2',
                                          file_name=self.file.name, overwrite=True)
        self.assertEqual(self.file.name, new_file.name)

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

    # Rename, Move and Copy
    def test_rename_file(self):
        new_name = 'renamed %s' % self.file.name
        self.file.name = new_name
        self.assertTrue(self.file.save())
        self.assertEqual(self.file.name, new_name)
        self.assertEqual(self.file.account, self.account.id)

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
    def test_put_file(self):
        self.file.update(file_data='hello there')
        self.assertTrue(self.file.contents().text == 'hello there')

    # Delete
    def test_delete_file(self):
        try:
            self.file.delete(permanent=True)
            read_file = self.account.files.retrieve(self.file.id)
        except sdk.exceptions.KloudlessException, e:
            error_data = json.loads(str(e).split('Error data: ')[1])
            self.assertEqual(error_data['status_code'], 404)

    @utils.allow(services=['box', 'egnyte', 'gdrive'])
    def test_properties(self):
        def parse(properties):
            result = {}
            for prop in properties['properties']:
                result[prop['key']] = prop['value']
            return result

        self.file.properties.delete_all()
        # Test PATCH
        time.sleep(0.5)
        properties = self.file.properties.update(data=[
            {
                'key': 'key1',
                'value': 'value1'
            },
            {
                'key': 'key2',
                'value': 'value2'
            }
        ])

        properties = parse(properties)
        self.assertEqual(len(properties), 2)
        self.assertEqual(properties['key1'], 'value1')
        self.assertEqual(properties['key2'], 'value2')

        time.sleep(0.5)
        self.file.properties.update(data=[
            {
                'key': 'key1', # delete property
                'value': None
            },
            {
                'key': 'key2', # update property
                'value': 'hello'
            },
            {
                'key': 'key3', # add property
                'value': 'value3'
            }
        ])

        # Test GET
        time.sleep(0.5)
        properties = parse(self.file.properties.all())
        self.assertEqual(len(properties), 2)
        self.assertEqual(properties['key2'], 'hello')
        self.assertEqual(properties['key3'], 'value3')

        # Test DELETE
        self.file.properties.delete_all()
        time.sleep(0.5)
        properties = parse(self.file.properties.all())
        self.assertEqual(len(properties), 0)

    @utils.allow(services=['s3'])
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
