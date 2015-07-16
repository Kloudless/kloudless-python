import kloudless
import unittest
import os
import utils

API_KEY = os.environ['API_KEY']
kloudless.configure(api_key=API_KEY)

accounts = utils.get_account_for_each_service()

class Users(unittest.TestCase):
    
    users = None

    def setUp(self):
        self.users = self.account.users.all()

    def not_admin(self):
        return not self.account.admin

    def test_list_users(self):
        if self.not_admin():
            return
        self.assertTrue(self.users)
        self.assertGreater(len(self.users), 0)
        self.assertEqual(type(self.users[0]), kloudless.resources.User)

    def test_retrieve_user(self):
        if self.not_admin():
            return
        user = self.account.users.retrieve(self.users[0].id)
        self.assertEqual(type(user), kloudless.resources.User)
        self.assertEqual(user.id, self.users[0].id)
    
    def test_user_membership(self):
        if self.not_admin():
            return
        for user in self.users:
            groups = user.get_groups()
            for group in groups:
                self.assertIsInstance(group, kloudless.resources.Group)

if __name__ == '__main__':
    suite = utils.create_suite([utils.create_test_case(acc, Users) for acc in accounts])
    unittest.TextTestRunner(verbosity=2).run(suite)
