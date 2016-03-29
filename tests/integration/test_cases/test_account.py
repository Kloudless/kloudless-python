import utils
import sdk
from sdk import exceptions as kexceptions

import unittest
import pytz
import time
import random
from datetime import datetime, timedelta


class Account(unittest.TestCase):
    def test_retrieve_account(self):
        account = sdk.Account(id=self.account.id)
        account.refresh()
        self.assertTrue(account.account)
        account = sdk.Account.retrieve(id=self.account.id)
        self.assertTrue(account.account)

    def _import(self, service='s3', **extra):
        return sdk.Account.create(
            account='test %s' % random.randint(0, 10e8), token='test',
            service=service, **extra)

    @utils.accounts_wide
    def test_list_accounts(self):
        accounts = utils.get_account_for_each_service()
        self.assertGreater(len(accounts), 0)
        self.assertEqual(len(sdk.Account.all(page=1, page_size=1)), 1)
        self.assertEqual(len(sdk.Account.all(page=2, page_size=1)), 1)
        self.assertEqual(len(sdk.Account.all(page=1, page_size=2)), 2)
        for acc in sdk.Account.all(active=True, page_size=1000):
            self.assertTrue(acc.active)
        for acc in sdk.Account.all(admin=True, page_size=100):
            self.assertTrue(acc.admin)

    @utils.accounts_wide
    def test_import_account(self):
        for s in ['hubspot', 'alfresco']:
            acc = None
            try:
                with self.assertRaises(kexceptions.APIException) as e:
                    acc = self._import(service=s)
            finally:
                if acc:
                    acc.delete()

        accounts = []
        try:
            accounts.append(self._import())
            accounts.append(self._import(service='sharepoint',
                                         domain='domain'))
            accounts.append(self._import(service='alfresco',
                                         repository_url='test'))
            accounts.append(self._import(service='hubspot', hub_id='hub'))
            for acc in accounts:
                self.assertTrue(acc.id)
        finally:
            for acc in accounts:
                acc.delete()

    @utils.accounts_wide
    def test_delete_account(self):
        account = self._import()
        account.delete()
        with self.assertRaises(AttributeError) as e:
            account.account
        time.sleep(1)
        with self.assertRaises(kexceptions.APIException) as e:
            sdk.Account.retrieve(account.id)
        with self.assertRaises(kexceptions.APIException) as e:
            sdk.Account(id=account.id).delete()
        self.assertTrue(e.exception.status, 404)

    @utils.accounts_wide
    def test_update_account(self):
        account = self._import()
        try:
            account_id = account.id
            account.token = 'test2'
            expiry = (datetime.utcnow() + timedelta(hours=1)).replace(
                tzinfo=pytz.utc)
            account.token_expiry = expiry
            account.save()
            self.assertEqual(account.id, account_id)
            self.assertEqual(account.token_expiry, expiry)
            account = sdk.Account.retrieve(id=account.id)
            self.assertEqual(account.id, account_id)
            self.assertEqual(account.token_expiry, expiry)

            account.service = 'invalid'
            with self.assertRaises(kexceptions.APIException) as e:
                account.save()
        finally:
            account.delete()

    def test_convert(self):
        account = sdk.Account.retrieve(id=self.account.id)
        contents = account.folders().contents()
        if contents:
            obj = contents[0]
            data = {}
            data['raw_id'] = obj.raw_id
            data['type'] = obj.type
            response = account.convert(data=data)
            self.assertTrue('id' in response)

    def test_file_upload_url(self):
        account = sdk.Account.retrieve(id=self.account.id)
        contents = account.folders().contents()
        name = 'test_file_name'
        if contents:
            obj = contents[0]
            data = {}
            data['parent_id'] = obj.id
            data['name'] = name
            response = account.file_upload_url(data=data)
            self.assertEqual(response['method'], 'put')
            self.assertTrue('url' in response)


def test_cases():
    return [utils.create_test_case(acc, Account) for acc in utils.accounts]

if __name__ == '__main__':
    suite = utils.create_suite(test_cases())
    unittest.TextTestRunner(verbosity=2).run(suite)
