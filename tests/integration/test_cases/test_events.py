import kloudless
import unittest
import os
import utils
import time

# seconds to wait for find_recent to run
WAIT_TIME = 1

SUPPORTED_SERVICES = ['dropbox', 'box', 'gdrive', 'skydrive', 'evernote',
                      'sharepoint', 'onedrivebiz', 'sharefile', 'egnyte',
                      'cmis', 'alfresco', 'salesforce', 'hubspot']

class Events(unittest.TestCase):

    # Perform events on folder
    @classmethod
    def setUpClass(self):
        self.test_folder = utils.create_or_get_test_folder(self.account)
        self.test_subfolder = self.account.folders.create(
                parent_id=self.test_folder.id, name='Test Events')
        self.test_subfolder2 = self.account.folders.create(
                parent_id=self.test_folder.id, name='Test Events2')

    def setUp(self):
        self.cursor = self.get_latest_cursor()
        self.file = utils.create_test_file(self.account, folder=self.test_folder)

    def update_events(self):
        utils.trigger_find_recent(self.account)
        time.sleep(WAIT_TIME)

    def get_latest_cursor(self):
        cursor = self.account.events.latest_cursor(self.account)
        if isinstance(cursor, dict):
            raise self.failureException("Unable to get latest cursor: %s" % cursor)
        return cursor

    def get_most_recent_event(self, cursor=0):
        self.update_events()
        events = self.account.events.all(cursor=cursor)
        while events.remaining:
            events = self.account.events.all(cursor=events.cursor)
        if events:
            return events[-1]
        else:
            raise self.failureException('No events found in the event stream.')

    # PARAMETER TESTS

    def test_event_page_size(self):
        events = self.account.events.all(page_size=1)
        self.assertEqual(len(events), 1)

    def test_event_invalid_page_size(self):
        with self.assertRaises(kloudless.exceptions.APIException):
            self.account.events.all(page_size=100000)

    def test_event_cursor(self):
        events = self.account.events.all(page_size=1)
        self.assertGreater(events.remaining, 0)

    def test_get_latest_cursor(self):
        self.assertIsInstance(self.cursor, int)

    ###############
    # NORMAL EVENTS
    ###############

    # ADD
    def test_add(self):
        event = self.get_most_recent_event(self.cursor)
        self.assertEqual(event.metadata.id, self.file.id)
        self.assertEqual(event.type, 'add')

    # DELETE
    def test_delete(self):
        file_id = self.file.id
        self.file.delete(permanent=True)
        event = self.get_most_recent_event(self.cursor)
        self.assertEqual(event.metadata.id, file_id)
        self.assertEqual(event.type, 'delete')

    # Commented out until Python SDK supports file updates.
    # # UPDATE
    # def test_update(self):
    #     # TODO: Update the file
    #     event = self.get_most_recent_event()
    #     self.assertEqual(event.metadata.id, self.file.id)
    #     self.assertEqual(event.type, 'update')


    # RENAME
    def test_rename(self):
        self.file.name = 'renamed-file.txt'
        self.file.save()
        event = self.get_most_recent_event(self.cursor)
        self.assertEqual(event.metadata.id, self.file.id)
        self.assertEqual(event.type, 'rename')

    # MOVE
    def test_move(self):
        self.file.parent_id = self.test_subfolder.id
        self.file.save()
        event = self.get_most_recent_event(self.cursor)
        self.assertEqual(event.metadata.id, self.file.id)
        self.assertEqual(event.type, 'move')

    ###################
    # TODO: ENTERPRISE EVENTS
    # Need the Python SDK to support enterprise actions.
    ###################

if __name__ == '__main__':
    suite = utils.create_suite(([utils.create_test_case(acc, Events) for
            acc in utils.accounts if acc.service in SUPPORTED_SERVICES]))
    unittest.TextTestRunner(verbosity=2).run(suite)
