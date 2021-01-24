from datetime import datetime, timezone
from unittest import TestCase

from src.container import Enclosure, Episode, Feed, Source
from src.rss_builder import create_rss


class CreateRssTestCase(TestCase):

    def test(self):
        expected_string = (
            b'<?xml version=\'1.0\' encoding=\'utf-8\'?>\n<rss xmlns:atom='
            b'"http://www.w3.org/2005/Atom" xmlns:itunes="http://www.itunes.'
            b'com/dtds/podcast-1.0.dtd">\n  <channel>\n    <title>Feed title</'
            b'title>\n    <link>Feed link</link>\n    <itunes:explicit>no</it'
            b'unes:explicit>\n    <description>feed description</description>'
            b'\n    <last_build_date>Sat, 24 Dec 2022 22:58:27 +0000</last_bu'
            b'ild_date>\n    <itunes:image href="http://image.jpg"/>\n    '
            b'<itunes:author>singlefeed</itunes:author>\n    <item>\n      '
            b'<title>Title 1</title>\n      <enclosure length="26229027" '
            b'type="audio/mpeg" url="https://example.com/1.mp3"/>\n      '
            b'<link>https://example.com/episode</link>\n      <guid>https://'
            b'example.com/episode</guid>\n      <pubDate>Sat, 24 Dec 2022 '
            b'22:58:27 +0000</pubDate>\n      <description>Item description'
            b'</description>\n      <itunes:duration>27:20</itunes:duration>\n'
            b'      <itunes:explicit>no</itunes:explicit>\n      <itunes:image'
            b' href="https://example.com/_3000px.jpg"/>\n      <author>Feed\'s'
            b' author</author>\n    </item>\n  </channel>\n</rss>\n'
        )
        feed = Feed(
            name='Feed name',
            title='Feed title',
            link='Feed link',
            language='ru',
            description='feed description',
            image='Feed image',
            sources=[Source('source1'), Source('source2')],
            last_build_date=datetime(
                2022, 12, 24, 22, 58, 27, tzinfo=timezone.utc
            ),
            episodes=[
                Episode(
                    title='Title 1',
                    enclosure=Enclosure(
                        length='26229027',
                        type='audio/mpeg',
                        url='https://example.com/1.mp3'
                    ),
                    link='https://example.com/episode',
                    published=datetime(
                        2022, 12, 24, 22, 58, 27, tzinfo=timezone.utc
                    ),
                    description='Item description',
                    duration='27:20',
                    image='https://example.com/_3000px.jpg',
                    author="Feed's author",
                    ),
            ],
        )
        url_for_feed_image = 'http://image.jpg'
        self.assertEqual(expected_string, create_rss(feed, url_for_feed_image))
