import kloudless
import unittest
import os
import utils
import time

# seconds to wait for find_recent to run
WAIT_TIME = 3

CUSTOM_WAIT_TIMES = {
    'sharepoint': 360,
    'onedrivebiz': 120,
    'box': 10,
}

LIMITED_EVENTS_SERVICES = ['gdrive']

SUPPORTED_SERVICES = ['dropbox', 'box', 'gdrive', 'skydrive', 'evernote',
                      'sharepoint', 'onedrivebiz', 'sharefile', 'egnyte',
                      'cmis', 'alfresco', 'salesforce', 'hubspot']

class Events(unittest.TestCase):

    # Perform events on folder
    @classmethod
    def setUpClass(self):
        self.wait_time = CUSTOM_WAIT_TIMES.get(self.account.service, WAIT_TIME)
        self.test_folder = utils.create_or_get_test_folder(self.account)
        self.test_subfolder = self.account.folders.create(
                parent_id=self.test_folder.id, name='Test Events')
        self.test_subfolder2 = self.account.folders.create(
                parent_id=self.test_folder.id, name='Test Events2')

    def setUp(self):
        self.cursor = self.get_latest_cursor()
        self.file = utils.create_test_file(self.account, folder=self.test_folder)

    def tearDown(self):
        self.file.delete()

    def update_events(self):
        utils.trigger_find_recent(self.account)
        time.sleep(self.wait_time)

    def get_latest_cursor(self):
        cursor = self.account.events.latest_cursor()
        if isinstance(cursor, dict):
            raise self.failureException("Unable to get latest cursor: %s" % cursor)
        return cursor

    def get_most_recent_events(self, cursor=0, return_one=False, retry=2):
        self.update_events()
        events = self.account.events.all(cursor=cursor)
        while events.remaining:
            events = self.account.events.all(cursor=events.cursor)
        if events:
            if return_one:
                return events[-1]
            else:
                return events
        else:
            if retry > 0:
                return self.get_most_recent_events(cursor, return_one, retry-1)
            raise self.failureException("No events found in the event stream "
                    "using cursor %s." % cursor)

    @staticmethod
    def _get_nested_dict_value(dictionary, keys):
        """
        Returns a nested value in a dictionary using a list of keys.
        """
        for i, key in enumerate(keys):
            if i + 1 == len(keys):
                return dictionary[key]
            else:
                dictionary = dictionary[key]

    def filter_events(self, events, filter_dict, expect_one=False):
        """
        Returns only events matching the filter_dict.
        Nested values are separated by `.` (e.g. `metadata.id`)
        Possible values are given in lists: ['possible', 'values']
        If expect_one is True, checks to see if only one event passes
         the filter and returns the single event.
        """
        events_to_return = events
        for k, v in filter_dict.iteritems():
            if isinstance(v, str):
                v = [v]
            events_to_return = ([event for event in events_to_return if
                self._get_nested_dict_value(event, k.split('.')) in v])
        if expect_one:
            self.assertEqual(len(events_to_return), 1)
            if events_to_return:
                return events_to_return[0]
        return events_to_return

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

    # def test_event_order(self):
    #     events = self.get_most_recent_events()
    #     last_modified = events[0]['modified']
    #     for event in events[1:]:
    #         current_modified = event['modified']
    #         self.assertGreaterEqual(last_modified, current_modified)
    #         last_modified = current_modified

    ###############
    # NORMAL EVENTS
    ###############

    # ADD
    def test_add(self):
        events = self.get_most_recent_events(self.cursor)
        event_filter = {
                'metadata.id': self.file.id,
                'type': 'add',
                }
        event = self.filter_events(events, event_filter, expect_one=True)
        if event:
            self.assertEqual(event.metadata.id, self.file.id)
            self.assertEqual(event.type, 'add')

    # DELETE
    def test_delete(self):
        file_id = self.file.id
        resp = self.file.delete()
        events = self.get_most_recent_events(self.cursor)
        event_filter = {
                'id': self.file.id,
                'type': 'delete',
                }
        event = self.filter_events(events, event_filter, expect_one=True)
        if event:
            self.assertEqual(event.id, file_id)
            self.assertEqual(event.type, 'delete')

    # Commented out until Python SDK supports file updates.
    # # UPDATE
    # def test_update(self):
    #     # TODO: Update the file
    #     event = self.get_most_recent_events(self.cursor, return_one=True)
    #     self.assertEqual(event.metadata.id, self.file.id)
    #     self.assertEqual(event.type, 'update')


    # RENAME
    def test_rename(self):
        self.file.name = 'renamed-file.txt'
        self.file.save()
        events = self.get_most_recent_events(self.cursor)
        event_filter = {
                'metadata.id': self.file.id,
                'type': 'rename',
                }
        if self.account.service in LIMITED_EVENTS_SERVICES:
            event_filter['type'] = 'add'
        event = self.filter_events(events, event_filter, expect_one=True)
        if event:
            self.assertEqual(event.metadata.id, self.file.id)
            if self.account.service in LIMITED_EVENTS_SERVICES:
                self.assertEqual(event.type, 'add')
            else:
                self.assertEqual(event.type, 'rename')

    # MOVE
    def test_move(self):
        self.file.parent_id = self.test_subfolder.id
        self.file.save()
        events = self.get_most_recent_events(self.cursor)
        event_filter = {
                'metadata.id': self.file.id,
                'type': 'move',
                }
        if self.account.service in LIMITED_EVENTS_SERVICES:
            event_filter['type'] = 'add'
        event = self.filter_events(events, event_filter, expect_one=True)
        if event:
            self.assertEqual(event.metadata.id, self.file.id)
            if self.account.service in LIMITED_EVENTS_SERVICES:
                self.assertEqual(event.type, 'add')
            else:
                self.assertEqual(event.type, 'move')

    ###################
    # TODO: ENTERPRISE EVENTS
    # Need the Python SDK to support enterprise actions.
    ###################

if __name__ == '__main__':
    suite = utils.create_suite(([utils.create_test_case(acc, Events) for
            acc in utils.accounts if acc.service in SUPPORTED_SERVICES]))
    unittest.TextTestRunner(verbosity=2).run(suite)
