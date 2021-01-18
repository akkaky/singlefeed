from unittest import TestCase

from src.container import Episode, Feed
from src.rss_builder import create_rss


class CreateRssTestCase(TestCase):

    def test(self):
        expected_string = (
            b'<?xml version=\'1.0\' encoding=\'utf-8\'?>\n<rss xmlns:atom='
            b'"http://www.w3.org/2005/Atom" xmlns:itunes="http://www.itunes.'
            b'com/dtds/podcast-1.0.dtd">\n  <channel>\n    <title>Feed title</'
            b'title>\n    <link>Feed link</link>\n    <itunes:explicit>no</it'
            b'unes:explicit>\n    <description>feed description</description>'
            b'\n    <last_build_date>Thu, 24 Dec 2022 22:58:27 +0000</last_bu'
            b'ild_date>\n    <itunes:image href="Feed image"/>\n    <itunes:a'
            b'uthor>singlefeed</itunes:author>\n    <item>\n      <title>Title'
            b' 1</title>\n      <enclosure length="26229027" type="audio/mpeg"'
            b' url="https://example.com/1.mp3"/>\n      <link>https://example.'
            b'com/episode</link>\n      <guid>https://example.com/episode</gu'
            b'id>\n      <pubDate>Thu, 24 Dec 2020 22:58:27 +0000</pubDate>\n '
            b'     <description>Item description</description>\n      <itunes:'
            b'duration>27:20</itunes:duration>\n      <itunes:explicit>no</itu'
            b'nes:explicit>\n      <itunes:image href="https://example.com/_30'
            b'00px.jpg"/>\n      <author>Feed\'s author</author>\n    </item>'
            b'\n  </channel>\n</rss>\n'
        )
        feed = Feed(
            name='Feed name',
            title='Feed title',
            link='Feed link',
            language='ru',
            description='feed description',
            image='Feed image',
            sources='source1, source2',
            last_build_date='Thu, 24 Dec 2022 22:58:27 +0000',
            episodes=[
                Episode(
                    title='Title 1',
                    enclosure={
                        'length': '26229027',
                        'type': 'audio/mpeg',
                        'url': 'https://example.com/1.mp3'
                    },
                    link='https://example.com/episode',
                    published='Thu, 24 Dec 2020 22:58:27 +0000',
                    description='Item description',
                    duration='27:20',
                    image='https://example.com/_3000px.jpg',
                    author="Feed's author",
                    ),
            ],
        )
        self.assertEqual(expected_string, create_rss(feed))
