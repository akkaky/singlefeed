import logging

from datetime import datetime, timedelta, timezone
from unittest import TestCase
from unittest.mock import patch

from src.date_normalize import (
string_to_datetime, datetime_to_string, normalize_timezone
)


class StringToDateTestCase(TestCase):

    def test__utc_timezone(self):
        input_string = 'Fri, 11 Dec 2020 11:55:40 +0000'
        self.assertEqual(
            datetime(2020, 12, 11, 11, 55, 40, tzinfo=timezone.utc),
            string_to_datetime(input_string),
        )

    def test__non_utc_timezone(self):
        input_string1 = 'Fri, 11 Dec 2020 11:55:40 +0300'
        input_string2 = 'Fri, 11 Dec 2020 11:55:40 -0500'
        self.assertEqual(
            datetime(
                2020, 12, 11, 11, 55, 40,
                tzinfo=timezone(timedelta(seconds=10800))
            ),
            string_to_datetime(input_string1),
        )
        self.assertEqual(
            datetime(
                2020, 12, 11, 11, 55, 40,
                tzinfo=timezone(timedelta(days=-1, seconds=68400))
            ),
            string_to_datetime(input_string2),
        )

    @patch('src.date_normalize.string_to_datetime')
    def test__logger(self, get_mock):
        get_mock.side_effect = ValueError
        with self.assertLogs() as cm:
            string_to_datetime('test')
        self.assertEqual(
            cm.output,
            [
                "ERROR:src.date_normalize:time data 'test' does not match "
                "format '%a, %d %b %Y %H:%M:%S %z'"
            ]
        )


class NormalizeTimezoneTestCase(TestCase):

    def test__normalize_timezone(self):
        input_strings = [
            'Fri, 11 Dec 2020 11:55:40 +0000',
            'Fri, 11 Dec 2020 11:55:40 EST',
            'Fri, 11 Dec 2020 11:55:40 PDT',
            'Fri, 11 Dec 2020 11:55:40 PST',
        ]
        expected_result = [
            'Fri, 11 Dec 2020 11:55:40 +0000',
            'Fri, 11 Dec 2020 11:55:40 -0500',
            'Fri, 11 Dec 2020 11:55:40 -0700',
            'Fri, 11 Dec 2020 11:55:40 -0800',
        ]
        self.assertEqual(
            expected_result,
            [normalize_timezone(string) for string in input_strings],
        )
