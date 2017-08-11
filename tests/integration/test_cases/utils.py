import unittest
import random
import os
import sys
import imp
from functools import wraps
import requests

# To handle package name changes
curdir = os.path.dirname(os.path.realpath(__file__))
setup_file = imp.load_source(
    'setup', os.path.join(curdir, '..', '..', '..', 'setup.py'))
sys.modules['sdk'] = __import__(setup_file.package_name)

import dynamic_case_module
import sdk

API_KEY = os.environ.get('API_KEY')
DEV_KEY = os.environ.get('DEV_KEY')
BASE_URL = os.environ.get('BASE_URL')

if not BASE_URL:
    BASE_URL = 'https://api.kloudless.com'

sdk.configure(api_key=API_KEY, dev_key=DEV_KEY, base_url=BASE_URL)
sdk.BaseResource._api_session = requests.Session()

def create_or_get_test_folder(account, parent_id='root', name=None):
    test_folders = dynamic_case_module.test_folders

    if account.id in test_folders:
        return test_folders[account.id]

    if not name:
        name = u't\xe9st folder %s' % random.randint(0, 10e8)

    folder = account.folders.retrieve(id=parent_id)

    # Find the first folder that supports folder creation within it and
    # create the test folder in it.

    stack = [folder]
    while stack:
        folder_to_check = stack.pop(0)
        if folder_to_check.can_create_folders:
            new_folder = account.folders.create(data={
                'parent_id': folder_to_check.id, 'name': name})
            break
        folders = folder_to_check.contents()
        # add at the beginning for a DFS / stack
        stack[0:0] = folders
    else:
        raise sdk.exceptions.KloudlessException(
            'Cannot find a parent folder to create the test folder in.')

    test_folders[account.id] = new_folder
    return new_folder


def create_test_file(account, folder=None, file_name=None,
                     file_data='test', overwrite=True):
    if not file_name:
        file_name = u't\xe9st file %s.txt' % random.randint(0, 10e8)
    if not folder:
        folder = create_or_get_test_folder(account)
    return account.files.create(file_name=file_name, parent_id=folder.id,
                                file_data=file_data, params={'overwrite': overwrite})


def is_resource_present(resource_type, resource_name, parent_folder):
    contents = parent_folder.contents()
    return resource_name in [f.name for f in contents if
                             f.type == resource_type]


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
    for acc in sdk.Account.all(active=True, page_size=1000):
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
    account_capabilities = {}
    account_apis = {}
    for acc in accounts:
        account_metadata = acc.retrieve(id=acc.id, retrieve_full=True)
        account_apis[acc.id] = account_metadata.get('apis', [])

        properties = account_metadata.get('properties')
        if properties:
            capabilities_dict = properties.get('capabilities', {})
        else:
            capabilities_dict = {}

        capabilities_list = []
        if capabilities_dict:
            for cap, val in capabilities_dict.iteritems():
                if val and val['value']:
                    capabilities_list.append(cap)
            account_capabilities[acc.id] = capabilities_list
        else:
            account_capabilities[acc.id] = capabilities_list


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

            if ((services_to_include and
                 current_service not in services_to_include)
                or (services_to_exclude and
                    current_service in services_to_exclude)
                or (env_services_to_include and
                    current_service not in env_services_to_include)):
                setattr(test, 'setUp',
                        lambda: test.skipTest('Reason: test is excluded.'))

    return unittest.TestSuite(suites)


def allow(services=[], services_to_exclude=[], apis=[], capabilities=[]):
    """
    Decorator to explicitly specify which services to run the decorated
    test on.
    'services' specifies the services the test should run on.
    'services_to_exclude' specifies the services the test should skip.
    Note: The actual include/exclude logic is in create_suite().
    """

    def allow_decorator(func):
        @wraps(func)
        def test_method(*args, **kwargs):
            self = args[0]

            if (services and services_to_exclude):
                raise ValueError("Please specify 'services' or "
                         "'services_to_exclude'")

            if account_apis.get(self.account.id):
                for api in apis:
                    if api not in account_apis[self.account.id]:
                        self.skipTest("%s not in list of apis." % api)

            if account_capabilities.get(self.account.id):
                for capability in capabilities:
                    if capability not in account_capabilities[self.account.id]:
                        self.skipTest("%s not in %s account's capabilities." %
                                      (capability, self.account.service))

            if (hasattr(self, 'account') and self.account and
                    self.account.service):
                if services and self.account.service not in services:
                    self.skipTest("%s not in list of included services." %
                                  self.account.service)
                elif (services_to_exclude and
                        self.account.service in services_to_exclude):
                    self.skipTest("%s in list of excluded services." %
                                  self.account.service)
            elif not (hasattr(self, 'account')):
                self.skipTest("No account so skipping.")

            return func(*args, **kwargs)
        return test_method
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
            if ((not hasattr(self, 'account') or
                 self.account.service in services) and
                    not os.environ.get('RUN_LONG_TESTS')):
                raise unittest.SkipTest('Reason: test takes too long.')
            return func(*args, **kwargs)
        return test_case_wrapper
    return test_case


def create_test_case(account, test_case):
    test_case_class_name = 'test_%s_%s_%s' % (
        test_case.__name__, account.service, account.id)
    class_attrs = {
        'account': account,
        'tearDownClass': gen_tear_down_class(test_case),
    }
    new_test_case = type(str(test_case_class_name), (test_case,), class_attrs)

    # Store the test class in a module, for nose to find it.
    # Also alias the module name based on the package we appear to be in.

    setattr(dynamic_case_module, test_case_class_name, new_test_case)
    sys.modules['integration.test_cases.dynamic_case_module'] = dynamic_case_module

    # Provide the context for nose.
    new_test_case.context = new_test_case
    new_test_case.__module__ = dynamic_case_module.__name__

    return new_test_case


def gen_tear_down_class(base_class):
    @classmethod
    def tearDownClass(cls):
        test_folders = dynamic_case_module.test_folders
        if cls.account.id in test_folders:
            test_folders[cls.account.id].delete(recursive=True)
            del test_folders[cls.account.id]
        super(cls, cls).tearDownClass()
    return tearDownClass
