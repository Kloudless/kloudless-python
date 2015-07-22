import kloudless
from kloudless.exceptions import KloudlessException as KException

import unittest
import random
import os
import time

API_KEY = os.environ.get('API_KEY')
DEV_KEY = os.environ.get('DEV_KEY')
BASE_URL = os.environ.get('BASE_URL')
if not BASE_URL:
    BASE_URL = 'https://api.kloudless.com'

kloudless.configure(api_key=API_KEY, dev_key=DEV_KEY, base_url=BASE_URL)


test_folders = {}
test_list = []
def create_or_get_test_folder(account, parent_id='root', name=None):
    if account.service in test_folders:
        return test_folders[account.service]
    if not name:
        name = u't\xe9stFolder %s' % random.randint(0, 10**8)
        storeFolder = True
    new_folder = None
    folder = account.folders.retrieve(id=parent_id)
    stack = [folder]
    test_folders[account.service] = folder
    while stack:
        folder_to_check = stack.pop(0)
        if folder_to_check.can_create_folders:
            new_folder = account.folders.create(parent_id=folder_to_check.id, name=name)
            break
        folders = folder_to_check.contents()
        # add at the beginning for a DFS / stack
        stack[0:0] = folders
    if new_folder is None:
        raise KException('Cannot find parent folder to create test folder')
    if storeFolder:
        test_folders[account.service] = new_folder
    return new_folder

def create_test_file(account, folder=None, file_name=u't\xe9st file.txt',
                     file_data='test'):
    if not folder:
        folder = create_or_get_test_folder(account)
    return account.files.create(file_name=file_name, parent_id=folder.id,
        file_data=file_data, overwrite=True)

def is_folder_present(folder_name, parent_folder):
  contents = parent_folder.contents()
  return folder_name in [f.name for f in contents if f.type == 'folder']

def get_account_for_each_service():
    services_to_exclude = []
    accounts = []
    services_to_include = os.environ.get('SERVICES', '').split(',')
    for acc in kloudless.Account.all(active=True, page_size=100):
        if acc.service in services_to_exclude:
            continue
        if any(services_to_include) and acc.service not in services_to_include:
            continue
        accounts.append(acc)
        services_to_exclude.append(str(acc.service))
    return accounts

if API_KEY:
    accounts = get_account_for_each_service()

def create_suite(test_cases):
    suites = []
    test_loader = unittest.TestLoader()
    test_loader.sortTestMethodsUsing = (
        lambda x,y : cmp(test_list.index(x), test_list.index(y))
        if x in test_list and y in test_list else None)
    for case in test_cases:
        suites.append(test_loader.loadTestsFromTestCase(case))
    return unittest.TestSuite(suites)

def create_test_case(account, test_case):
    return type('test_' + test_case.__name__ + '_' + str(account.service),
        (test_case,), {'account' : account,
                       'tearDownClass': clean_up,
                        })

def accounts_wide(func):
    """
    Decorator to indicate that the test case should only be run once across
    all accounts.
    """
    def test_case(*args, **kwargs):
        if test_case._already_ran:
            return
        return func(*args, **kwargs)
    test_case._already_ran = False
    return test_case

def skip_long_test(services=[]):
    """
    Decorator to determine whether to run long tests or not.
    """
    def test_case(func):
        def test_case_wrapper(*args, **kwargs):
            self = args[0]
            if (self.account.service in services and
                not os.environ.get('RUN_LONG_TESTS')):
                return
            return func(*args, **kwargs)
        return test_case_wrapper
    return test_case

def order(func):
    test_list.append(func.__name__)
    return func


@classmethod
def clean_up(cls):
    if cls.account.service in test_folders:
        test_folders[cls.account.service].delete(recursive=True)
        del test_folders[cls.account.service]

