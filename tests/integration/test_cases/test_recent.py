import unittest
import os
import random
import time

import utils
import sdk

class Recent(unittest.TestCase):

    def setUp(self):
        acc = self.account
        self.test_file_1 = utils.create_test_file(acc, file_name='recent1.txt',
            file_data=str(random.random()))
        self.test_file_2 = utils.create_test_file(acc, file_name='recent2.txt',
            file_data=str(random.random()))

    def test_retrieve_recent(self):
        time.sleep(0.5)
        results = self.account.recent.all()
        for i in xrange(len(results)-1):
            self.assertGreaterEqual(results[i].modified, results[i+1].modified)

    def test_recent_page_size(self):
        results = self.account.recent.all(page_size=1)
        self.assertEqual(len(results), 1)

    def test_bad_recent_page_size(self):
        with self.assertRaises(sdk.exceptions.APIException) as e:
            self.account.recent.all(page_size=1001)

    def test_simple_recent_page(self):
        acc = self.account
        test_file_3 = utils.create_test_file(acc, file_name='recent3.txt',
            file_data=str(random.random()))
        time.sleep(0.5)
        results = acc.recent.all(page_size=1, page=1)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].id, test_file_3.id)

    def test_complex_recent_page(self):
        acc = self.account
        files = {}
        for i in xrange(1, 11):
            files['test_file_{0}'.format(i)] = utils.create_test_file(acc, file_name='p{0}'.format(i),
                file_data=str(random.random()))
        time.sleep(0.5)
        results = acc.recent.all(page_size=3, page=1)
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0].id, files['test_file_10'].id)
        self.assertEqual(results[1].id, files['test_file_9'].id)
        self.assertEqual(results[2].id, files['test_file_8'].id)

        results = acc.recent.all(page_size=3, page=4)
        self.assertEqual(results[0].id, files['test_file_1'].id)

    def test_bad_recent_page(self):
        with self.assertRaises(sdk.exceptions.APIException) as e:
            self.account.recent.all(page_size=1, page=0)

    def test_outofbounds_recent_page(self):
        length = self.account.recent.all().total
        with self.assertRaises(sdk.exceptions.APIException) as e:
            self.account.recent.all(page_size=1, page=length+1)

    def test_bad_after_timestamp(self):
        self.assertEqual(self.account.recent.all(after="00/00/00"), [])

    def test_after_timestamp(self):
        acc = self.account
        test_file_4 = utils.create_test_file(acc, file_name='recent4.txt',
            file_data=str(random.random()))
        after = test_file_4.modified
        test_file_5 = utils.create_test_file(acc, file_name='recent5.txt',
            file_data=str(random.random()))
        time.sleep(2)
        results = acc.recent.all(after=after)
        self.assertEqual(len(results), 1)
        self.assertGreaterEqual(results[0].modified, after)

        results = acc.recent.all(after=test_file_5.modified)
        self.assertEqual(results, [])

if __name__ == '__main__':
    suite = utils.create_suite([utils.create_test_case(acc, Recent) for acc in utils.accounts])
    unittest.TextTestRunner(verbosity=2).run(suite)
