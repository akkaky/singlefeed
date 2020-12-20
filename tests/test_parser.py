from unittest import TestCase

from parser import _normalize_published


class ParserTestCase(TestCase):

    def test__normalize_published__RFC1123__RFC1123Z(self):
        input_data = 'Thu, 11 Apr 2019 15:37:31 EST'
        output_data = 'Thu, 11 Apr 2019 15:37:31 -0500'
        self.assertEqual(output_data, _normalize_published(input_data))
