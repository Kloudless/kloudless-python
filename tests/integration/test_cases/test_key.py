import kloudless
import unittest
import utils
import os

class Key(unittest.TestCase):

    def test_retrieve_account_key(self):
        result = None
        acc = self.account
        key = acc.keys.all()
        if not key:
            result = 'key not found'
        else:
            key = key[0]
            result = key.account
        self.assertEqual(result, acc.id)


if __name__ == '__main__':
    suite = utils.create_suite([utils.create_test_case(acc, Key) for acc in utils.accounts])
    unittest.TextTestRunner(verbosity=2).run(suite)