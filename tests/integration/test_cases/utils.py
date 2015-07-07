import kloudless
import unittest
import random
from kloudless.exceptions import KloudlessException as KException

test_folders = {}
def create_or_get_test_folder(account, parent_id='root', name=None):
    if account.service in test_folders:
        return test_folders[account.service]
    if not name:
        name = unicode('testFolder ' + str(random.randint(0, 10**8)))
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

def create_test_file(account, folder=None):
    if not folder:
        folder = create_or_get_test_folder(account)
    return account.files.create(file_name=unicode('t e s t.txt'), parent_id=folder.id,
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
        (test_case,), {'account' : account,
                       'tearDownClass': clean_up,
                        })

@classmethod
def clean_up(cls):
    if cls.account.service in test_folders:
        test_folders[cls.account.service].delete(recursive=True)
        del test_folders[cls.account.service]


