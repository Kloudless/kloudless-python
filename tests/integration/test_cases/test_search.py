import unittest
import os
import base64
import random
import time

import utils
import sdk

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
        q = base64.b64encode(os.urandom(40))
        self.assertEqual(self.account.search.all(q=q), [])

    def test_empty_str_search(self):
        with self.assertRaises(sdk.exceptions.APIException) as cm:
            self.account.search.all(q='')

    @utils.skip_long_test(services=['box'])
    def test_mult_results_search(self):
        acc = self.account
        test_file_name = 'search' + str(random.random())[2:] + '.txt'
        root_folder = utils.create_or_get_test_folder(acc)
        test_folder_1 = acc.folders.create(parent_id=root_folder.id,
                                           name='folder %s' % random.randint(0, 10e8))
        test_folder_2 = acc.folders.create(parent_id=root_folder.id,
                                           name='folder %s' % random.randint(0, 10e8))
        test_file_1 = utils.create_test_file(acc, folder=test_folder_1,
                                             file_name=test_file_name)
        test_file_2 = utils.create_test_file(acc, folder=test_folder_2,
                                             file_name=test_file_name)
        if acc.service == 'box':
            time.sleep(210)
        results = acc.search.all(q=test_file_name)
        self.assertEqual({results[0].id, results[1].id},
                         {test_file_1.id, test_file_2.id})

def test_cases():
    return [utils.create_test_case(acc, Search) for acc in utils.accounts]

if __name__ == '__main__':
    suite = utils.create_suite(test_cases())
    unittest.TextTestRunner(verbosity=2).run(suite)
