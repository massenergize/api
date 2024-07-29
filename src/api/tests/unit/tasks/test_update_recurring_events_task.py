import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

from _main_.utils.common import custom_timezone_info
from task_queue.database_tasks.update_recurring_events import (
    get_all_recurring_events,
    update_recurring_events,
    get_final_date,
    update_event_dates,
    update_weekly_event,
    update_monthly_event,
    get_date_of_first_weekday,
    handle_recurring_event_exception
)


class TestUpdateRecurringEvents(unittest.TestCase):
    @patch('task_queue.database_tasks.update_recurring_events.Event')
    def test_get_all_recurring_events(self, MockEvent):
        mock_query_set = MagicMock()
        MockEvent.objects.filter.return_value = mock_query_set
        result = get_all_recurring_events()
        MockEvent.objects.filter.assert_called_once_with(is_recurring=True, is_deleted=False, recurring_details__isnull=False)
        self.assertEqual(result, mock_query_set)

    @patch('task_queue.database_tasks.update_recurring_events.get_all_recurring_events')
    @patch('task_queue.database_tasks.update_recurring_events.parse_datetime_to_aware')
    @patch('task_queue.database_tasks.update_recurring_events.update_event_dates')
    @patch('task_queue.database_tasks.update_recurring_events.handle_recurring_event_exception')
    @patch('task_queue.database_tasks.update_recurring_events.get_final_date')
    def test_update_recurring_events(self, mock_get_final_date, mock_handle_recurring_event_exception, mock_update_event_dates, mock_parse_datetime_to_aware, mock_get_all_recurring_events):
        mock_event = MagicMock()
        mock_event.recurring_details = {'separation_count': 1}
        mock_event.start_date_and_time = datetime(2023, 1, 1)
        mock_get_all_recurring_events.return_value = [mock_event]
        mock_parse_datetime_to_aware.return_value = datetime(2023, 1, 2)
        mock_get_final_date.return_value = None

        result = update_recurring_events()
        mock_update_event_dates.assert_called_once_with(mock_event, datetime(2023, 1, 2))
        mock_handle_recurring_event_exception.assert_called_once_with(mock_event)
        self.assertTrue(result)

    def test_get_final_date(self):
        mock_event = MagicMock()
        mock_event.start_date_and_time = datetime(2023, 1, 1, 10, 0, 0)
        mock_event.recurring_details = {'final_date': '2023-01-10'}
        today = datetime(2023, 1, 2)
        result = get_final_date(mock_event, today)
        expected_date = datetime(2023, 1, 10, 10, 0, 0, tzinfo=custom_timezone_info())
        self.assertEqual(result, expected_date)

    @patch('task_queue.database_tasks.update_recurring_events.update_weekly_event')
    @patch('task_queue.database_tasks.update_recurring_events.update_monthly_event')
    def test_update_event_dates(self, mock_update_monthly_event, mock_update_weekly_event):
        mock_event = MagicMock()
        mock_event.recurring_details = {'recurring_type': 'week', 'separation_count': 1}
        today = datetime(2023, 1, 2)
        update_event_dates(mock_event, today)
        mock_update_weekly_event.assert_called_once()
        mock_update_monthly_event.assert_not_called()

    def test_update_weekly_event(self):
        mock_event = MagicMock()
        start_date = datetime(2023, 1, 1)
        duration = timedelta(hours=1)
        sep_count = 1
        today = datetime(2023, 1, 8)
        update_weekly_event(mock_event, start_date, duration, sep_count, today)
        self.assertEqual(mock_event.start_date_and_time, timedelta(weeks=1) + today)
        self.assertEqual(mock_event.end_date_and_time, timedelta(weeks=1) + today + duration)
        mock_event.save.assert_called_once()
    
    @patch('task_queue.database_tasks.update_recurring_events.get_date_of_first_weekday')
    def test_update_monthly_event(self, mock_get_date_of_first_weekday):
        mock_event = MagicMock()
        mock_event.recurring_details = {
            'recurring_type': 'month',
            'separation_count': 1,
            'day_of_week': 'Monday',
            'week_of_month': 'first'
        }
        start_date = datetime(2023, 1, 1, tzinfo=custom_timezone_info())
        duration = timedelta(hours=1)
        sep_count = 1
        today = datetime(2023, 2, 1, tzinfo=custom_timezone_info())
        mock_get_date_of_first_weekday.return_value = 1
        update_monthly_event(mock_event, start_date, duration, sep_count, today)
        self.assertEqual(mock_event.start_date_and_time, today + timedelta(weeks=4))
        self.assertEqual(mock_event.end_date_and_time, today + timedelta(weeks=4) + duration)
        mock_event.save.assert_called_once()

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