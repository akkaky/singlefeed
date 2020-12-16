from unittest import TestCase

from parser import ParserFeed


class ParserFeedTestCase(TestCase):

    def test__get_feed_dict(self):
        with open('tests/test_xml1.xml') as test_xml1, \
                open('tests/test_xml2.xml') as test_xml2, \
                open('tests/expected_result.txt') as file:
            parser = ParserFeed(test_xml1.read(), test_xml2.read())
            expected_result = file.read().strip()
            self.assertEqual(expected_result, str(parser.get_feeds_dict()))
