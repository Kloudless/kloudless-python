import kloudless
import unittest
import os
import utils

allow_multipart = ['azure', 's3', 'dropbox', 'egnyte', 'gdrive', 'skydrive', 
                'sharefile', 'sharepoint', 'onedrivebiz']
require_file_size = ['gdrive', 'egnyte', 'skydrive']

class Multipart(unittest.TestCase):
    num_parts = 3
    chunk_size = 5242880

    def test_multipart(self):
        if self.account.service not in allow_multipart:
            self.skipTest()

        # Create Multipart
        acc = self.account
        folder = utils.create_or_get_test_folder(acc)
        multipart_data = {
                "parent_id": folder.id,
                "name": "multipart_test"
                }
        if self.account.service in require_file_size:
            multipart_data["size"] = self.num_parts * self.chunk_size
        result = acc.multipart.create(data=multipart_data)
        multipart = result
        
        # Upload Chunk
        for x in range(1, self.num_parts+1):
            data = os.urandom(self.chunk_size)
            response = multipart.upload_chunk(part_number=x, data=data)
            self.assertTrue(response)
        
        # Complete
        file_result = multipart.complete()
        self.assertIsInstance(file_result, kloudless.resources.File)

        # Folder Check
        if file_result.get('parent'):
            if file_result.parent.get('name'):
                self.assertEqual(folder.name, file_result.parent.name)
            elif file_result.parent.get('id'):
                folder_metadata = acc.folders.retrieve(id=file_result.parent.id)
                folder_name = folder_metadata.get('name')
                if folder_name:
                    self.assertEqual(folder.name, folder_name)

        # Size Check
        if file_result.get('size'):
            total_size = self.num_parts * self.chunk_size
            self.assertEqual(total_size, file_result.get('size'))

if __name__ == '__main__':
    suite = utils.create_suite([utils.create_test_case(acc, Multipart) for acc in utils.accounts])
    unittest.TextTestRunner(verbosity=2).run(suite)
