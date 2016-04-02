import unittest

import utils
import sdk

change_file_permissions = ['gdrive']
change_folder_permissions = ['gdrive', 'box']
list_permissions = ['gdrive', 'box', 'sharepoint', 'onedrivebiz']
readonly_permissions = ['sharepoint', 'onedrivebiz']


class Permissions(unittest.TestCase):
    new_roles = {}

    @utils.allow(services=list_permissions)
    def setUp(self):
        acc = self.account
        if acc.service in list_permissions:
            self.test_folder = utils.create_or_get_test_folder(acc)
            self.test_file = utils.create_test_file(acc)

        new_roles = {
            "kloudless.nose.tester+1@gmail.com": "reader",
            "kloudless.nose.tester+2@gmail.com": "writer"
        }

        if acc.service in change_folder_permissions:
            self.new_roles = new_roles
            self.test_folder.permissions.create(data=self.new_roles)

        if acc.service in change_file_permissions:
            self.new_roles = new_roles
            self.test_file.permissions.create(data=self.new_roles)

    def list_helper(self, data):
        result = data.permissions.all()
        self.assertIsInstance(result, sdk.resources.AnnotatedList)
        owner_exists = False
        for perm in result:
            self.assertIsInstance(perm, sdk.resources.Permission)
            if self.account.service not in readonly_permissions:
                if perm.role == "owner":
                    owner_exists = True
                else:
                    self.assertIn(perm.email, self.new_roles)
                    self.assertEqual(perm.role, self.new_roles.get(perm.email))
                self.assertTrue(owner_exists)

    # Folder List
    def test_folder_permissions_list(self):
        if self.account.service in list_permissions:
            self.list_helper(self.test_folder)

    # Folder Set
    def test_folder_permissions_set(self):
        if self.account.service in change_folder_permissions:
            self.new_roles = {
                "kloudless.nose.tester+3@gmail.com": "reader",
                "kloudless.nose.tester+4@gmail.com": "writer"
            }
            result = self.test_folder.permissions.create(data=self.new_roles)
            self.assertIsInstance(result.permissions, list)
            self.list_helper(self.test_folder)

    # Folder Update
    def test_folder_permissions_update(self):
        if self.account.service in change_folder_permissions:
            self.new_roles.update({
                "kloudless.nose.tester+1@gmail.com": "writer",
                "kloudless.nose.tester+2@gmail.com": "reader",
                "kloudless.nose.tester+3@gmail.com": "writer",
                "kloudless.nose.tester+4@gmail.com": "reader"
            })
            result = self.test_folder.permissions.update(data=self.new_roles)
            self.assertIsInstance(result.permissions, list)
            self.list_helper(self.test_folder)

    # File List
    def test_file_permissions_list(self):
        if self.account.service in list_permissions:
            self.list_helper(self.test_file)

    # File Set
    def test_file_permissions_set(self):
        if self.account.service in change_file_permissions:
            self.new_roles = {
                "kloudless.nose.tester+3@gmail.com": "reader",
                "kloudless.nose.tester+4@gmail.com": "writer"
            }
            result = self.test_file.permissions.create(data=self.new_roles)
            self.assertIsInstance(result.permissions, list)
            self.list_helper(self.test_file)

    # File Update
    def test_file_permissions_update(self):
        if self.account.service in change_file_permissions:
            self.new_roles.update({
                "kloudless.nose.tester+1@gmail.com": "writer",
                "kloudless.nose.tester+2@gmail.com": "reader",
                "kloudless.nose.tester+3@gmail.com": "writer",
                "kloudless.nose.tester+4@gmail.com": "reader"
            })
            result = self.test_file.permissions.update(data=self.new_roles)
            self.assertIsInstance(result.permissions, list)
            self.list_helper(self.test_file)


def test_cases():
    return [utils.create_test_case(acc, Permissions) for acc in utils.accounts]

if __name__ == '__main__':
    suite = utils.create_suite(test_cases())
    unittest.TextTestRunner(verbosity=2).run(suite)
