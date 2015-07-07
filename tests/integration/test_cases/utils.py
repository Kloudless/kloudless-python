import kloudless
import unittest

def create_or_get_test_folder(account, parent_id='root', name='testFolder'):
    return account.folders.create(parent_id=parent_id, name=name)

def create_test_file(account, folder=None):
    if not folder:
        folder = create_or_get_test_folder(account)
    return account.files.create(file_name='test.txt', parent_id=folder.id,
        file_data='test', overwrite=True)

def get_account_for_each_service():
    services_to_exclude = []
    accounts = []
    for acc in kloudless.Account.all(active=True):
        if acc.service in services_to_exclude:
            continue
        accounts.append(acc)
        services_to_exclude.append(str(acc.service))

    return accounts

def create_suite(test_cases):
    suites = []
    for case in test_cases:
        suites.append(unittest.TestLoader().loadTestsFromTestCase(case))
    return unittest.TestSuite(suites)

def create_test_case(account, test_case):
    return type('test_' + test_case.__name__ + '_' + str(account.service),
        (test_case,), {'account' : account})
