import unittest
import random
import os
import time
import sys
import imp
from functools import wraps

# To handle package name changes
curdir = os.path.dirname(os.path.realpath(__file__))
setup = imp.load_source(
    'setup', os.path.join(curdir, '..', '..', '..', 'setup.py'))
sys.modules['sdk'] = __import__(setup.package_name)

import sdk

API_KEY = os.environ.get('API_KEY')
DEV_KEY = os.environ.get('DEV_KEY')
BASE_URL = os.environ.get('BASE_URL')
if not BASE_URL:
    BASE_URL = 'https://api.kloudless.com'

sdk.configure(api_key=API_KEY, dev_key=DEV_KEY, base_url=BASE_URL)


test_folders = {}

def create_or_get_test_folder(account, parent_id='root', name=None):
    if account.id in test_folders:
        return test_folders[account.id]
    if not name:
        name = u't\xe9stFolder %s' % random.randint(0, 10**8)
        storeFolder = True
    new_folder = None
    folder = account.folders.retrieve(id=parent_id)
    stack = [folder]
    test_folders[account.id] = folder
    while stack:
        folder_to_check = stack.pop(0)
        if folder_to_check.can_create_folders:
            new_folder = account.folders.create(parent_id=folder_to_check.id,
                                                name=name)
            break
        folders = folder_to_check.contents()
        # add at the beginning for a DFS / stack
        stack[0:0] = folders
    if new_folder is None:
        raise sdk.exceptions.KloudlessException(
            'Cannot find parent folder to create test folder')
    if storeFolder:
        test_folders[account.id] = new_folder
    return new_folder

def create_test_file(account, folder=None, file_name=u't\xe9st file.txt',
                     file_data='test', overwrite=True):
    if not folder:
        folder = create_or_get_test_folder(account)
    return account.files.create(file_name=file_name, parent_id=folder.id,
                                file_data=file_data, overwrite=overwrite)

def is_resource_present(resource_type, resource_name, parent_folder):
    contents = parent_folder.contents()
    return resource_name in [f.name for f in contents if f.type == resource_type]

def is_file_present(file_name, parent_folder):
    return is_resource_present('file', file_name, parent_folder)

def is_folder_present(folder_name, parent_folder):
    return is_resource_present('folder', folder_name, parent_folder)

def trigger_find_recent(account):
    """
    Triggers find_recent by updating the account.
    Only works if find_recent is enabled for that account.
    """
    account.save()

def get_account_for_each_service():
    services_to_exclude = []
    accounts = []
    services_to_include = os.environ.get('SERVICES', '').split(',')
    accounts_to_include = os.environ.get('ACCOUNTS', '').split(',')
    for acc in sdk.Account.all(active=True, page_size=100):
        if acc.service in services_to_exclude:
            continue
        if any(services_to_include) and acc.service not in services_to_include:
            continue
        if any(accounts_to_include) and str(acc.id) not in accounts_to_include:
            continue
        accounts.append(acc)
        services_to_exclude.append(str(acc.service))
    return accounts

if API_KEY:
    accounts = get_account_for_each_service()

def create_suite(test_cases):
    suites = []
    test_loader = unittest.TestLoader()
    for case in test_cases:
        suites.append(test_loader.loadTestsFromTestCase(case))

    env_services_to_include = []
    if os.environ.get('SERVICES', ''):
        env_services_to_include = os.environ.get('SERVICES', '').split(',')

    for suite in suites:
        for test in suite:
            if not hasattr(test, 'account'):
                continue
            current_service = test.account.service
            method_name = test.id().split('.')[-1]
            method = getattr(test, method_name)
            services_to_include = getattr(method, 'services_to_include', [])
            services_to_exclude = getattr(method, 'services_to_exclude', [])

            if ((services_to_include and current_service not in services_to_include)
                or (services_to_exclude and current_service in services_to_exclude)
                or (env_services_to_include and current_service not in env_services_to_include)):
                setattr(test, 'setUp', lambda: test.skipTest('Reason: test is excluded.'))

    return unittest.TestSuite(suites)

def create_test_case(account, test_case):
    return type('test_' + test_case.__name__ + '_' + str(account.service),
        (test_case,), {'account' : account,
                       'tearDownClass': clean_up,
                        })

def allow(services=[], services_to_exclude=[]):
    """
    Decorator to explicitly specify which services to run the decorated test on.
    'services' specifies the services the test should run on.
    'services_to_exclude' specifies the services the test should skip.
    Note: The actual include/exclude logic is in create_suite().
    """
    if (services and services_to_exclude
        or not services and not services_to_exclude):
        raise ValueError("Please specify 'services' or 'services_to_exclude', and not both")

    def allow_decorator(func):
        if services:
            func.services_to_include = services
        elif services_to_exclude:
            func.services_to_exclude = services_to_exclude
        return func
    return allow_decorator

def accounts_wide(func):
    """
    Decorator to indicate that the test case should only be run once across
    all accounts.
    """
    @wraps(func)
    def test_case(*args, **kwargs):
        if test_case._already_ran:
            raise unittest.SkipTest('Reason: test already ran once.')
        test_case._already_ran = True
        return func(*args, **kwargs)
    test_case._already_ran = False
    return test_case

def skip_long_test(services=[]):
    """
    Decorator to determine whether to run long tests or not.
    """
    def test_case(func):
        @wraps(func)
        def test_case_wrapper(*args, **kwargs):
            self = args[0]
            if ((not hasattr(self, 'account') or self.account.service in services) and
                not os.environ.get('RUN_LONG_TESTS')):
                raise unittest.SkipTest('Reason: test takes too long.')
            return func(*args, **kwargs)
        return test_case_wrapper
    return test_case


@classmethod
def clean_up(cls):
    if cls.account.id in test_folders:
        test_folders[cls.account.id].delete(recursive=True)
        del test_folders[cls.account.id]

