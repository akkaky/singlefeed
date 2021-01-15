import logging
import json
import sqlite3

from .container import Episode, Feed, FeedEpisodeJsonEncoder, create_episode


logger = logging.getLogger(__name__)

DATA_BASE = 'singlefeed.db'
FEED_ATTRIBUTES = ', '.join(list(Feed.__dict__['__dataclass_fields__'])[:-1])
EPISODE_ATTRIBUTES = (
    f'feed_name, {", ".join(Episode.__dict__["__dataclass_fields__"])}'
)


def create_connection():
    conn = None
    try:
        conn = sqlite3.connect(DATA_BASE)
    except sqlite3.Error as error:
        logger.error(error)
    return conn


def drop_tables(conn):
    for table_name in ('feeds', 'episodes'):
        conn.execute(f'DROP TABLE IF EXISTS {table_name}')
        logger.info(f'Table {table_name} dropped')


def create():
    with create_connection() as conn:
        drop_tables(conn)
        conn.execute(
            f'CREATE TABLE feeds({FEED_ATTRIBUTES})'
        )
        conn.execute(
            f'CREATE TABLE episodes({EPISODE_ATTRIBUTES})'
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


def get_feeds(name=None):
    with create_connection() as conn:
        if name:
            data = conn.execute(
                    f'SELECT * FROM feeds WHERE name = "{name}"'
            ).fetchone()
            if data:
                feed = Feed(*data)
                feed.episodes = get_episodes(feed.name, conn)
                return feed
            logger.critical(f"{name} doesn't exist in database")
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
