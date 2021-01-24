import logging
import json
import sqlite3
from typing import Union

from .container import (
    Episode, Feed, FeedEpisodeJsonEncoder, create_episode,
    get_container_attrs_keys,
)


logger = logging.getLogger(__name__)
database = 'singlefeed.db'


def create_connection():
    conn = None
    try:
        conn = sqlite3.connect(database)
    except sqlite3.Error as error:
        logger.error(error)
    return conn


def drop_tables(conn):
    for table_name in ('feeds', 'episodes'):
        conn.execute(f'DROP TABLE IF EXISTS {table_name}')


def create():
    with create_connection() as conn:
        drop_tables(conn)
        conn.execute(
            f'CREATE TABLE feeds({get_container_attrs_keys("Feed")})'
        )
        conn.execute(
            f'CREATE TABLE episodes({get_container_attrs_keys("Episode")})'
        )


def add_feed(feed: Feed):
    with create_connection() as conn:
        conn.execute(
            f'INSERT INTO feeds VALUES ({",".join("?" * 8)})',
            (*feed.get_attrs_values(),),
        )


def add_episodes(feed_name: str, episodes: list[Episode]):
    with create_connection() as conn:
        for episode in episodes:
            conn.execute(
                f'INSERT INTO episodes VALUES ({",".join("?" * 9)})',
                (feed_name, *episode.get_attrs_values()),
            )


def get_feeds(name=None) -> Union[Feed, None, list[Feed]]:
    with create_connection() as conn:
        if name:
            data = conn.execute(
                    f'SELECT * FROM feeds WHERE name = "{name}"'
            ).fetchone()
            if data:
                feed = Feed(*data)
                feed.episodes = get_episodes(feed.name, conn)
                return feed
            logger.error(f"'{name}' does not exist in database")
            return None
        feeds = [Feed(*row) for row in conn.execute('SELECT * FROM feeds')]
        for feed in feeds:
            feed.episodes = get_episodes(feed.name, conn)
        return feeds


def get_episodes(feed_name, conn: sqlite3.Connection):
    return [
        create_episode(row[1:]) for row in conn.execute(
            f'SELECT * FROM episodes WHERE feed_name = "{feed_name}"'
        )
    ]


def update_last_build_date(feed: Feed):
    with create_connection() as conn:
        conn.execute(
            f'UPDATE feeds SET last_build_date = "{feed.last_build_date}" '
            f'WHERE name = "{feed.name}"'
        )


def json_load(file_name: str) -> dict:
    with open(file_name) as json_file:
        return json.load(json_file)


def json_dump(feed: Feed):
    with open(f'{feed.name}.json', 'w') as file:
        json.dump(feed, file, cls=FeedEpisodeJsonEncoder, indent=4)
        print(f'"{feed.name}.json" file created')
