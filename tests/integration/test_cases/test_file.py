import kloudless
import unittest
import utils
import os
import json
import time
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

    @utils.allow(services=['box', 'egnyte'])
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

if __name__ == '__main__':
    suite = utils.create_suite([utils.create_test_case(acc, File) for acc in utils.accounts])
    unittest.TextTestRunner(verbosity=2).run(suite)
