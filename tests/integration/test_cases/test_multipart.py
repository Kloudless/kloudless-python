import kloudless
import unittest
import os
import utils

class Multipart(unittest.TestCase):
    pass

if __name__ == '__main__':
    suite = utils.create_suite([utils.create_test_case(acc, Multipart) for acc in utils.accounts])
    unittest.TextTestRunner(verbosity=2).run(suite)
