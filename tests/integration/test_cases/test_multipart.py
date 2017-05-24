import unittest
import os
import math

import utils
import sdk

allow_multipart = ['azure', 's3', 'dropbox', 'egnyte', 'gdrive', 'skydrive',
                   'sharefile', 'sharepoint', 'onedrivebiz']
require_file_size = ['gdrive', 'egnyte', 'skydrive']


class Multipart(unittest.TestCase):
    file_size = 15728640  # 15 MB

    @utils.allow(apis=['storage'],
                 capabilities=['multipart_uploads_supported_for_files'])
    def test_multipart(self):
        if self.account.service not in allow_multipart:
            self.skipTest("Multipart not allowed.")

        # Create Multipart
        acc = self.account
        folder = utils.create_or_get_test_folder(acc)
        multipart_data = {
            "parent_id": folder.id,
            "name": "multipart_test"
        }
        if self.account.service in require_file_size:
            multipart_data["size"] = self.file_size
        multipart = acc.multipart.create(data=multipart_data)

        # Retrieve Multipart
        new_multipart = acc.multipart.retrieve(id=multipart.id)
        self.assertEqual(str(new_multipart.id), str(multipart.id))
        self.assertEqual(str(new_multipart.account), str(multipart.account))

        chunk_size = new_multipart['part_size']
        num_parts = int(math.ceil(1.0 * self.file_size / chunk_size))

        # Upload Chunk
        for x in range(1, num_parts + 1):
            data = os.urandom(min(chunk_size,
                                  self.file_size - chunk_size * (x - 1)))
            response = multipart.upload_chunk(part_number=x, data=data)
            self.assertTrue(response)

        # Complete
        file_result = multipart.complete()
        self.assertIsInstance(file_result, sdk.resources.File)

        # Folder Check
        if file_result.get('parent'):
            if file_result.parent.get('name'):
                self.assertEqual(
                    folder.name.lower(), file_result.parent.name.lower())
            elif file_result.parent.get('id'):
                folder_metadata = acc.folders.retrieve(
                    id=file_result.parent.id)
                folder_name = folder_metadata.get('name')
                if folder_name:
                    self.assertEqual(folder.name, folder_name)

        # Size Check
        if file_result.get('size'):
            self.assertEqual(self.file_size, file_result.get('size'))

        # Overwrite Checks

        multipart_data["size"] = 1 * chunk_size

        multipart = acc.multipart.create(
            data=multipart_data, params={'overwrite': 'true'})
        response = multipart.upload_chunk(
            part_number=1, data=os.urandom(chunk_size))
        self.assertTrue(response)
        overwrite_file_result = multipart.complete()
        self.assertIsInstance(overwrite_file_result, sdk.resources.File)
        self.assertEqual(file_result.name, overwrite_file_result.name)

        multipart = acc.multipart.create(
            data=multipart_data, params={'overwrite': 'false'})
        response = multipart.upload_chunk(
            part_number=1, data=os.urandom(chunk_size))
        self.assertTrue(response)
        no_overwrite_file_result = multipart.complete()
        self.assertIsInstance(overwrite_file_result, sdk.resources.File)
        self.assertNotEqual(file_result.name, no_overwrite_file_result.name)


def test_cases():
    return [utils.create_test_case(acc, Multipart) for acc in utils.accounts]


if __name__ == '__main__':
    suite = utils.create_suite(test_cases())
    unittest.TextTestRunner(verbosity=2).run(suite)
