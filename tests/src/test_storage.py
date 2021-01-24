import tempfile
import sqlite3
from unittest import TestCase
from unittest.mock import MagicMock

import src
from src.container import Episode, Feed
from src.storage import (
    add_episodes, add_feed, create, drop_tables, get_episodes, get_feeds
)


create_feeds_table_string = (
    'CREATE TABLE feeds(name, title, link, language, description, image, '
    'sources, last_build_date)'
)
create_episodes_table_string = (
    'CREATE TABLE episodes(feed_name, title, enclosure, link, published, '
    'description, duration, image, author)'
)
select_tables_names = 'SELECT name FROM sqlite_master WHERE type="table"'
episode = Episode(
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
feed = Feed(
    name='Feed name',
    title='Feed title',
    link='Feed link',
    language='ru',
    description='feed description',
    image='Feed image',
    sources='source1, source2',
    last_build_date='Thu, 24 Dec 2022 22:58:27 +0000',
    episodes=[episode],
)


class DropTablesTestCase(TestCase):

    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile()
        self.conn = sqlite3.connect(self.temp_db.name)
        src.storage.create_connection = MagicMock(
            return_value=self.conn
        )
        self.conn.execute(create_feeds_table_string)
        self.conn.execute(create_episodes_table_string)

    def tearDown(self) -> None:
        self.conn.close()

    def test(self):
        drop_tables(self.conn)
        self.assertListEqual(
            [],
            [
                str(*table) for table in self.conn.execute(
                    select_tables_names
                ).fetchall()
            ],
        )


class CreateTestCase(TestCase):

    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile()
        self.conn = sqlite3.connect(self.temp_db.name)
        src.storage.create_connection = MagicMock(
            return_value=self.conn
        )

    def tearDown(self) -> None:
        self.conn.close()

    def test(self):
        create()
        self.assertListEqual(
            ['feeds', 'episodes'],
            [
                str(*table) for table in self.conn.execute(
                    select_tables_names
                ).fetchall()
            ],
        )


class AddEpisodeTestCase(TestCase):

    def setUp(self) -> None:
        self.temp_db = tempfile.NamedTemporaryFile()
        self.conn = sqlite3.connect(self.temp_db.name)
        src.storage.create_connection = MagicMock(
            return_value=self.conn
        )
        self.conn.execute(create_episodes_table_string)

    def tearDown(self):
        self.conn.close()

    def test(self):
        add_episodes(feed.name, [episode])
        expected_result = (
            'Feed name',
            'Title 1',
            '26229027, audio/mpeg, https://example.com/1.mp3',
            'https://example.com/episode',
            'Thu, 24 Dec 2020 22:58:27 +0000',
            'Item description',
            '27:20',
            'https://example.com/_3000px.jpg',
            "Feed's author",
        )
        result = self.conn.execute(
            f'SELECT * FROM episodes WHERE feed_name = "{feed.name}"'
        ).fetchall()
        self.assertTupleEqual(expected_result, *result)


class AddFeedTestCase(TestCase):

    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile()
        self.conn = sqlite3.connect(self.temp_db.name)
        src.storage.create_connection = MagicMock(
            return_value=self.conn
        )
        self.conn.execute(create_feeds_table_string)

    def tearDown(self):
        self.conn.close()

    def test(self):
        add_feed(feed)
        expected_result = [
            (
                'Feed name', 'Feed title', 'Feed link', 'ru',
                'feed description', 'Feed image', 'source1, source2',
                'Thu, 24 Dec 2022 22:58:27 +0000',
            )
        ]
        result = self.conn.execute(
            f'SELECT * FROM feeds WHERE name = "{feed.name}"'
        ).fetchall()
        self.assertEqual(expected_result, result)


class GetEpisodesTestCase(TestCase):

    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile()
        self.conn = sqlite3.connect(self.temp_db.name)
        src.storage.create_connection = MagicMock(
            return_value=self.conn
        )
        self.conn.execute(create_episodes_table_string)
        self.conn.execute(
            f'INSERT INTO episodes VALUES ({",".join("?" * 9)})',
            (
                'Feed name', 'Title 1',
                '26229027, audio/mpeg, https://example.com/1.mp3',
                'https://example.com/episode',
                'Thu, 24 Dec 2020 22:58:27 +0000',
                'Item description', '27:20', 'https://example.com/_3000px.jpg',
                "Feed's author",
            ),
        )

    def tearDown(self):
        self.conn.close()

    def test(self):
        result = get_episodes(feed.name, self.conn)
        self.assertListEqual(feed.episodes, result)


class GetFeedsTestCase(TestCase):

    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile()
        self.conn = sqlite3.connect(self.temp_db.name)
        src.storage.create_connection = MagicMock(
            return_value=self.conn
        )
        self.conn.execute(create_feeds_table_string)
        self.conn.execute(create_episodes_table_string)
        self.conn.execute(
            f'INSERT INTO feeds VALUES ({",".join("?" * 8)})',
            (
                'Feed name', 'Feed title', 'Feed link', 'ru',
                'feed description', 'Feed image', 'source1, source2',
                'Thu, 24 Dec 2022 22:58:27 +0000',
            ),
        )
        self.conn.execute(
            f'INSERT INTO episodes VALUES ({",".join("?" * 9)})',
            (
                'Feed name', 'Title 1',
                '26229027, audio/mpeg, https://example.com/1.mp3',
                'https://example.com/episode',
                'Thu, 24 Dec 2020 22:58:27 +0000',
                'Item description', '27:20',
                'https://example.com/_3000px.jpg',
                "Feed's author",
            ),
        )

    def tearDown(self):
        self.conn.close()

    def test__return_all_feeds(self):
        result = get_feeds()
        self.assertListEqual([feed], result)

    def test__return_none(self):
        with self.assertLogs() as cm:
            result = get_feeds('Wrong name')
        self.assertIsNone(result)
        self.assertEqual(
            cm.output,
            ["ERROR:src.storage:'Wrong name' does not exist in database"]
        )

    def test__name_in_args(self):
        result = get_feeds('Feed name')
        self.assertEqual(feed, result)
