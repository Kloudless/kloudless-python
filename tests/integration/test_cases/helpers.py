import os
import time


def permission_testing(self, instance):
    # GET Permissions of File
    permissions = instance.permissions.all()

    # Assertion
    self.assertEqual(len(permissions), 1)
    for permission in permissions:
        self.assertEqual(permission['role'], 'owner')
        self.assertEqual(permission['type'], 'permission')

    # Create Permissions of File
    if os.environ.get('SHARE_USER_EMAIL'):
        permissions = [{
            'type': 'user',
            'role': 'reader',
            'email': os.environ.get('SHARE_USER_EMAIL')
        }]
        instance.permissions.create(data=permissions)
        time.sleep(0.5)

        # Assertion
        permissions = instance.permissions.all()
        self.assertEqual(len(permissions), 2)
        for permission in permissions:
            self.assertIn(permission['role'], ['owner', 'reader'])
            self.assertEqual(permission['type'], 'permission')

        # Update Permissions of File
        permissions = [{
            'type': 'user',
            'role': 'writer',
            'email': os.environ.get('SHARE_USER_EMAIL')
        }]
        instance.permissions.update(data=permissions)
        time.sleep(0.5)

        # Assertion
        permissions = instance.permissions.all()
        self.assertEqual(len(permissions), 2)
        for permission in permissions:
            self.assertIn(permission['role'], ['owner', 'writer'])
            self.assertEqual(permission['type'], 'permission')

    # Test Update to clear all extra Permissions of File
    permissions = []
    instance.permissions.create(data=permissions)
    time.sleep(0.5)

    # Assertion
    permissions = instance.permissions.all()
    self.assertEqual(len(permissions), 1)
    for permission in permissions:
        self.assertEqual(permission['role'], 'owner')
        self.assertEqual(permission['type'], 'permission')
