import unittest
import zoneinfo
from datetime import datetime

from _main_.utils.common import parse_datetime_to_aware


class TestParseDatetimeToTimezoneAware(unittest.TestCase):
	
	def setUp(self):
		self.datetime_str = '2022-02-20 10:20:30'
		self.timezone_str = 'America/New_York'
	
	def tearDown(self):
		pass
	
	def test_parse_datetime_to_aware_without_parameters(self):
		result = parse_datetime_to_aware()
		expected_timezone = zoneinfo.ZoneInfo('UTC')
		self.assertIsNotNone(result)
		self.assertEqual(result.tzinfo, expected_timezone)
		
	def test_parse_datetime_to_aware_with_datetime_and_timezone_str(self):
		result = parse_datetime_to_aware(self.datetime_str, self.timezone_str)
		expected_naive_datetime = datetime.strptime(self.datetime_str, '%Y-%m-%d %H:%M:%S')
		expected_timezone = zoneinfo.ZoneInfo(self.timezone_str)
		expected_aware_datetime = expected_naive_datetime.replace(tzinfo=expected_timezone)
		
		self.assertIsNotNone(result)
		self.assertEqual(result, expected_aware_datetime)
		self.assertEqual(result.tzinfo,expected_timezone)
	
	def test_parse_datetime_to_aware_with_no_datetime_str(self):
		result = parse_datetime_to_aware('', self.timezone_str)
		self.assertIsNotNone(result)
		self.assertEquals(result.tzinfo, zoneinfo.ZoneInfo(self.timezone_str))
	
	def test_parse_datetime_to_aware_with_invalid_timezone_str(self):
		result = parse_datetime_to_aware(self.datetime_str, 'America/Invalid')
		self.assertIsNone(result)


if __name__ == '__main__':
	unittest.main()
