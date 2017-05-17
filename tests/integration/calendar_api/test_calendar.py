import unittest
import os

# Add parent dir to path to import utils
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__),
                '..')))
from test_cases import utils


class Calendar(unittest.TestCase):

    @utils.allow(services=['google_calendar'])
    def setUp(self):
        self.test_calendar_data = {
            "name": "My Test Calendar",
            "description": "A test calendar for testing",
            "location": "San Francisco, CA",
            "timezone": "US/Pacific"
        }
        self.test_calendar = self.account.calendars.create(data=self.test_calendar_data)
        self.test_event_data = {
            "name": "Test Event",
            "start": "2017-09-01T12:30:00Z",
            "end": "2017-09-01T13:30:00Z",
            "creator": {
                "name": "Company Owner",
                "email": "owner@company.com"
            },
            "owner": {
                "name": "Company Owner",
                "email": "owner@company.com"
            }
        }
        self.test_event = self.test_calendar.events.create(data=self.test_event_data)

    @utils.allow(services=['google_calendar'])
    def tearDown(self):
        self.test_event.delete()
        self.test_calendar.delete()

    @utils.allow(services=['google_calendar'])
    def test_list_calendar(self):
        test_calendars = self.account.calendars.all()
        # Assertion
        if test_calendars:
            test_calendar = test_calendars[0]
            self.assertEqual(int(test_calendar.account_id), self.account.id)

    @utils.allow(services=['google_calendar'])
    def test_list_event(self):
        test_events = self.test_calendar.events.all()
        # Assertion
        if test_events:
            test_event = test_events[0]
            self.assertEqual(int(test_event.account_id), self.account.id)
            self.assertEqual(test_event.calendar_id, self.test_calendar.id)

    @utils.allow(services=['google_calendar'])
    def test_read_calendar(self):
        test_calendar = self.account.calendars.retrieve(self.test_calendar.id)

        # Assertion
        self.assertEqual(test_calendar.id, self.test_calendar.id)
        self.assertEqual(test_calendar.account_id, self.test_calendar.account_id)
        self.assertEqual(test_calendar.name, self.test_calendar.name)
        self.assertEqual(test_calendar.description, self.test_calendar.description)
        self.assertEqual(test_calendar.location, self.test_calendar.location)

    @utils.allow(services=['google_calendar'])
    def test_read_event(self):
        test_event = self.test_calendar.events.retrieve(id=self.test_event.id)

        # Assertion
        self.assertEqual(test_event.id, self.test_event.id)
        self.assertEqual(test_event.account_id, self.test_event.account_id)
        self.assertEqual(test_event.calendar_id, self.test_event.calendar_id)
        self.assertEqual(test_event.name, self.test_event.name)
        self.assertEqual(test_event.description, self.test_event.description)
        self.assertEqual(test_event.end, self.test_event.end)
        self.assertEqual(test_event.start, self.test_event.start)
        self.assertEqual(test_event.attendees, self.test_event.attendees)
        self.assertEqual(test_event.organizer, self.test_event.organizer)
        self.assertEqual(test_event.attachments, self.test_event.attachments)

    @utils.allow(services=['google_calendar'])
    def test_update_calender(self):
        test_calendar = self.test_calendar
        test_calendar.name = 'My Test Calendar updated'
        test_calendar.description = 'A test calendar for testing updated'
        test_calendar.save()
        self.assertEqual('My Test Calendar updated', test_calendar.name)
        self.assertEqual('A test calendar for testing updated', test_calendar.description)

    @utils.allow(services=['google_calendar'])
    def test_update_event(self):
        test_event = self.test_event
        test_event.name = 'Test Event Updated'
        test_event.start = '2017-09-01T12:00:00Z'
        test_event.end = '2017-09-01T13:00:00Z'
        test_event.save()
        self.assertEqual('Test Event Updated', test_event.name)
        self.assertEqual('2017-09-01T12:00:00Z', test_event.start)
        self.assertEqual('2017-09-01T13:00:00Z', test_event.end)

def test_cases():
    return [utils.create_test_case(acc, Calendar) for acc in utils.accounts]

if __name__ == '__main__':
    suite = utils.create_suite(test_cases())
    unittest.TextTestRunner(verbosity=2).run(suite)
