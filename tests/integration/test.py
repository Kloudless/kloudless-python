import unittest
import os
import inspect
import sys

from test_cases import *
from management_api import *
from crm_api import *

STORAGE_SERVICES = ['dropbox', 'box', 'gdrive', 'skydrive', 'sharefile',
                    'copy', 'sugarsync', 'egnyte', 'evernote', 'sharepoint',
                    'onedrivebiz', 'cmis', 'alfresco', 'alfresco_cloud',
                    'salesforce', 'hubspot', 'smb', 'jive', 'webdav', 'cq5',
                    's3', 'azure']
CRM_SERVICES = ['salesforce', 'dynamics', 'oracle']


def test_cases():
    management_tests = []
    storage_tests = []
    crm_tests = []

    for m in sys.modules.keys():
        if '.test_' in m:
            for name, cls in inspect.getmembers(sys.modules[m],
                                                inspect.isclass):
                if '.test_' in cls.__module__:
                    if 'management_api' in cls.__module__:
                        management_tests.append(cls)
                    if 'crm_api' in cls.__module__:
                        crm_tests.append(cls)
                    if 'test_cases.' in cls.__module__:
                        storage_tests.append(cls)

    cases = []
    if utils.DEV_KEY:
        cases.extend(management_tests)

    if utils.API_KEY:
        for acc in utils.accounts:
            if acc.service in STORAGE_SERVICES:
                for storage_test in storage_tests:
                    cases.append(utils.create_test_case(acc, storage_test))

            if acc.service in CRM_SERVICES:
                for crm_test in crm_tests:
                    cases.append(utils.create_test_case(acc, crm_test))

    return cases

if __name__ == '__main__':
    suite = utils.create_suite(test_cases())
    unittest.TextTestRunner(verbosity=2).run(suite)
