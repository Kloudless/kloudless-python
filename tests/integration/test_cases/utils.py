import kloudless
import unittest
from kloudless.exceptions import KloudlessException as KException

def create_or_get_test_folder(account, parent_id='root', name='testFolder'):
    # TODO: add search for 'testFolder' when we have search for folders
    new_folder = None
    folder = account.folders.retrieve(id=parent_id)
    stack = [folder]
    while stack:
        folder_to_check = stack.pop(0)
        if folder_to_check.can_create_folders:
            new_folder = folder_to_check
            break
        folders = folder_to_check.contents()
        # add at the beginning for a DFS / stack
        stack[0:0] = folders
    if new_folder is None:
        # throw exception
        raise KException('Cannot find parent folder to create test folder')
    return account.folders.create(parent_id=new_folder.id, name=name)

def create_test_file(account, folder=None):
    # TODO: add alternative to check for `can_upload_files`
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
