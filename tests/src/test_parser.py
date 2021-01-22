from unittest import TestCase

from lxml import etree

import src.parser as parser
from src.parser import get_episodes, logger
from src.container import Episode


CORRECT_RSS = """
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom" 
  xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd">
  <channel>
    <atom:link href="https://example.com" rel="self" 
      type="application/rss+xml"/>
    <title>Feed's title</title>
    <pubDate>Thu, 24 Dec 2020 22:58:27 +0000</pubDate>
    <lastBuildDate>Fri, 15 Jan 2021 06:53:10 +0000</lastBuildDate>
    <link>https://example.com</link>
    <language>ru</language>
    <itunes:summary></itunes:summary>
    <image>
      <url>https://example.com/3000px.jpg</url>
      <title>Feed's title</title>
      <link>https://example.com/</link>
    </image>
    <itunes:author>Feed's author</itunes:author>
    <itunes:image href="https://example.com/3000px.jpg" />
    <description>Feed's description</description>
    <item>
      <title>Title 1</title>
      <itunes:title>Title 1</itunes:title>
      <pubDate>Thu, 24 Dec 2020 22:58:27 +0000</pubDate>
      <guid>https://example.com/1.mp3</guid>
      <link>https://example.com/episode</link>
      <itunes:image href="https://example.com/_3000px.jpg" />
      <description>Item description</description>
      <enclosure length="26229027" type="audio/mpeg" 
        url="https://example.com/1.mp3" />
      <itunes:duration>27:20</itunes:duration>
      <itunes:author>Feed's author</itunes:author>
    </item>
  </channel>
</rss>
"""
ITEM_EMPTY_TAGS = etree.XML('<item></item>')


class GetEpisodesTestCase(TestCase):

    def setUp(self) -> None:
        self.correct_episodes_list = [
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
            )
        ]

    def test__correct_rss(self):
        self.assertEqual(
            self.correct_episodes_list,
            [
                Episode(**dictionary) for dictionary in
                get_episodes(CORRECT_RSS)
            ],
        )

    def test__parse_title__empty_tag__empty_str(self):
        with self.assertLogs(logger) as cm:
            self.assertEqual('', parser._parse_title(ITEM_EMPTY_TAGS))
        self.assertEqual(cm.output, ["WARNING:src.parser:Can't parse 'title'"])

    def test__parse_enclosure__empty_tag__empty_str(self):
        with self.assertLogs(logger) as cm:
            self.assertEqual('', parser._parse_enclosure(ITEM_EMPTY_TAGS))
        self.assertEqual(
            cm.output, ["WARNING:src.parser:Can't parse 'enclosure'"],
        )

    def test__parse_link_empty_tag_in_item(self):
        item_empty_link_tag = etree.XML(
            '<rss><channel><link>https://example.com</link><item></item>'
            '</channel></rss>'
        )
        for item in item_empty_link_tag.iter('item'):
            self.assertEqual(
                'https://example.com',
                parser._parse_link(item),
            )

    def test__parse_published__empty_tag__empty_str(self):
        with self.assertLogs(logger) as cm:
            self.assertEqual('', parser._parse_published(ITEM_EMPTY_TAGS))
        self.assertEqual(
            cm.output, ["WARNING:src.parser:Can't parse 'pubDate'"],
        )

    def test__parse_description__empty_tag__empty_str(self):
        with self.assertLogs(logger) as cm:
            self.assertEqual('', parser._parse_description(ITEM_EMPTY_TAGS))
        self.assertEqual(
            cm.output, ["WARNING:src.parser:Can't parse 'description'"],
        )

    def test__parse_duration__empty_tag__empty_str(self):
        with self.assertLogs(logger) as cm:
            self.assertEqual('', parser._parse_duration(ITEM_EMPTY_TAGS))
        self.assertEqual(
            cm.output, ["WARNING:src.parser:Can't parse 'duration'"],
        )

    def test__parse_image__empty_tag(self):
        image_tag_in_header = etree.XML(
            '<rss ><channel><image><url>some image</url></image><item></item>'
            '</channel></rss>'
        )
        itunes_image_tag_in_header = etree.XML(
            '<rss xmlns:itunes = "http://www.itunes.com/dtds/podcast-1.0.dtd">'
            '<channel><itunes:image href="another image"/><item></item>'
            '</channel></rss>'
        )
        self.assertEqual(
            parser._parse_image(image_tag_in_header), 'some image',
        )
        self.assertEqual(
            parser._parse_image(itunes_image_tag_in_header), 'another image',
        )
