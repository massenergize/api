import unittest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, Mock, patch

from _main_.utils.common import custom_timezone_info
from task_queue.database_tasks.update_recurring_events import get_date_of_first_weekday, get_final_date, \
    handle_recurring_event_exception, update_event_dates, update_monthly_event


class TestRecurringEventsUtils(unittest.TestCase):

    def setUp(self):
        self.event = Mock()
        self.event.start_date_and_time = datetime(2023, 1, 1, 10, 0, 0, tzinfo=custom_timezone_info())
        self.event.end_date_and_time = datetime(2023, 1, 1, 12, 0, 0, tzinfo=custom_timezone_info())
        self.today = datetime(2023, 1, 15, tzinfo=custom_timezone_info())
        self.duration = timedelta(hours=2)

    def test_get_final_date_valid(self):
        self.event.recurring_details = {'final_date': '2023-01-10'}
        expected_date = datetime(2023, 1, 10, 10, 0, 0, tzinfo=custom_timezone_info())
        result = get_final_date(self.event, self.today)
        self.assertEqual(result, expected_date)

    def test_get_final_date_none(self):
        self.event.recurring_details = {'final_date': 'None'}
        result = get_final_date(self.event, self.today)
        self.assertIsNone(result)

    def test_get_final_date_not_present(self):
        self.event.recurring_details = {}
        result = get_final_date(self.event, self.today)
        self.assertIsNone(result)

    @patch('task_queue.database_tasks.update_recurring_events.update_weekly_event')
    def test_update_event_dates_weekly(self, mock_update_weekly_event):
        self.event.recurring_details = {'separation_count': '1', 'recurring_type': 'week'}
        update_event_dates(self.event, self.today)
        mock_update_weekly_event.assert_called_once()

    @patch('task_queue.database_tasks.update_recurring_events.update_monthly_event')
    def test_update_event_dates_monthly(self, mock_update_monthly_event):
        self.event.recurring_details = {'separation_count': '1', 'recurring_type': 'month'}
        update_event_dates(self.event, self.today)
        mock_update_monthly_event.assert_called_once()

    @patch('task_queue.database_tasks.update_recurring_events.get_date_of_first_weekday', return_value=1)
    def test_update_monthly_event(self, mock_get_date_of_first_weekday):
        sep_count = 1
        self.event.recurring_details = {'day_of_week': 'Monday', 'week_of_month': 'first'}
        update_monthly_event(self.event, self.event.start_date_and_time, self.duration, sep_count, self.today)
        self.assertEqual(self.event.start_date_and_time, datetime(2023, 2, 1, 10, 0, 0, tzinfo=custom_timezone_info()))
        self.assertEqual(self.event.end_date_and_time, datetime(2023, 2, 1, 12, 0, 0, tzinfo=custom_timezone_info()))

    def test_get_date_of_first_weekday(self):
        new_month = datetime(2023, 1, 1)
        day_of_week = 'Monday'
        result = get_date_of_first_weekday(new_month, day_of_week)
        self.assertEqual(result, 2)  # 2nd January 2023 is a Monday

    @patch('task_queue.database_tasks.update_recurring_events.RecurringEventException')
    def test_handle_recurring_event_exception(self, MockRecurringEventException):
        mock_event = MagicMock()
        mock_event.start_date_and_time = datetime(2023, 1, 1, 10, 0, 0, tzinfo=custom_timezone_info())

        mock_exception = MagicMock()
        mock_exception.former_time = datetime(2022, 12, 31, 10, 0, 0, tzinfo=custom_timezone_info())

        MockRecurringEventException.objects.filter.return_value.first.return_value = mock_exception

        handle_recurring_event_exception(mock_event)

        mock_exception.delete.assert_called_once()

if __name__ == '__main__':
    unittest.main()