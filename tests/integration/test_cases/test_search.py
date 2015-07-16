import kloudless
import unittest
import os
import utils
import random
import time

class Search(unittest.TestCase):

    @utils.skip_long_test(services=['box'])
    def test_simple_search(self):
        acc = self.account
        test_file_name = 'search' + str(random.random())[2:] + '.txt'
        test_file = utils.create_test_file(acc, file_name=test_file_name)
        if acc.service == 'box':
            time.sleep(210)
        results = acc.search.all(q=test_file_name)
        self.assertGreater(results, 0)
        if results:
            self.assertEqual(results[0].id, test_file.id)

    def test_bad_search(self):
        self.assertEqual(self.account.search.all(q='asdfghjkl'), [])

    def test_empty_str_search(self):
        with self.assertRaises(kloudless.exceptions.APIException) as e:
            self.account.search.all(q='')

    @utils.skip_long_test(services=['box'])
    def test_mult_results_search(self):
        acc = self.account
        test_file_name = 'search' + str(random.random())[2:] + '.txt'
        root_folder = utils.create_or_get_test_folder(acc)
        test_folder_1 = acc.folders.create(parent_id=root_folder.id, name='testFolder1')
        test_folder_2 = acc.folders.create(parent_id=root_folder.id, name='testFolder2')
        test_file_1 = utils.create_test_file(acc, folder=test_folder_1,
            file_name=test_file_name)
        test_file_2 = utils.create_test_file(acc, folder=test_folder_2,
            file_name=test_file_name)
        if acc.service == 'box':
            time.sleep(210)
        results = acc.search.all(q=test_file_name)
        self.assertEqual({results[0].id, results[1].id}, {test_file_1.id, test_file_2.id})

if __name__ == '__main__':
    suite = utils.create_suite([utils.create_test_case(acc, Search) for acc in utils.accounts])
    unittest.TextTestRunner(verbosity=2).run(suite)
