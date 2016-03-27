import unittest
import os

import utils
import sdk

class Group(unittest.TestCase):

    groups = None

    def setUp(self):
        self.groups = self.account.groups.all()

    def not_admin(self):
        return not self.account.admin

    def test_list_groups(self):
        if self.not_admin():
            return
        if not self.groups:
            return
        self.assertGreater(len(self.groups), 0)
        for group in self.groups:
            self.assertIsInstance(group, sdk.resources.Group)

    def test_retrieve_group(self):
        if self.not_admin():
            return
        if not self.groups:
            return
        group = self.account.groups.retrieve(self.groups[0].id)
        self.assertEqual(type(group), sdk.resources.Group)
        self.assertEqual(group.id, self.groups[0].id)

    def test_group_members(self):
        if self.not_admin():
            return
        for group in self.groups:
            users = group.get_users()
            for user in users:
                self.assertIsInstance(user, sdk.resources.User)

if __name__ == '__main__':
    suite = utils.create_suite([utils.create_test_case(acc, Group) for acc in utils.accounts])
    unittest.TextTestRunner(verbosity=2).run(suite)
