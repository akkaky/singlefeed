import logging
import yaml
import requests
import sys

from apscheduler.schedulers.background import BackgroundScheduler
from flask import (
    abort, Flask, Response, render_template, request, send_from_directory,
    url_for,
)

from src import parser
from src.container import Episode, Feed
from src.date_normalize import (
    normalize_timezone, string_to_datetime, datetime_to_string,
)
from src.rss_builder import create_rss
from src import storage


logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s',
)
logger = logging.getLogger(__name__)


def get_config() -> dict:
    try:
        with open('config.yaml') as s:
            return yaml.load(s, Loader=yaml.BaseLoader).values()
    except FileNotFoundError as e:
        logger.error(e)
        sys.exit()


def get_feed_attr_values(feed: dict) -> tuple[str, str, str, str, str, str]:
    title = feed.get('title')
    link = feed.get('link')
    language = feed.get('language')
    description = feed.get('description')
    image = feed.get('image')
    sources = ', '.join(feed.get('sources'))
    return title, link, language, description, image, sources


def create_feeds(feeds: dict) -> list[Feed]:
    feeds_list = []
    for name, feed in feeds.items():
        feed = Feed(name, *get_feed_attr_values(feed))
        if feed:
            logger.info(f'"{feed.name}" feed created.')
        else:
            logger.critical(f"Can't to create {name} feed")
        feeds_list.append(feed)
    return feeds_list


def sort_episodes(feed: Feed):
    if feed.last_build_date:
        feed.episodes.sort(
            key=lambda episode: string_to_datetime(episode.published),
            reverse=True,
        )


def add_new_episodes(feed: Feed, rss_: str) -> list:
    episodes = []
    for episode in parser.get_episodes(rss_):
        episode = Episode(**episode)
        if episode in feed.episodes:
            break
        episodes.append(episode)
    return episodes


def check_update(feed: Feed):
    new_episodes = []
    last_build_date_list = []
    logger.info(f'"{feed.name}" check updates...')
    for url in feed.sources.split(', '):
        rss_str = requests.get(url).text
        last_build_date = string_to_datetime(normalize_timezone(
            parser.get_last_build_date(rss_str)
        )
        )
        if last_build_date:
            last_build_date_list.append(last_build_date)
        if feed.last_build_date is None or (string_to_datetime(
                feed.last_build_date) < max(last_build_date_list)
        ):
            new_episodes.extend(add_new_episodes(feed, rss_str))
    if new_episodes:
        logger.info(f'"{feed.name}" {len(new_episodes)} new episodes added.')
        feed.last_build_date = datetime_to_string(max(last_build_date_list))
        storage.add_episodes(feed.name, new_episodes)
        storage.update_last_build_date(feed)
    else:
        logger.info(f'"{feed.name}" feed is up to date.')


def update_feeds():
    for feed in storage.get_feeds():
        check_update(feed)


def init() -> dict:
    feeds, settings = get_config()
    if feeds and settings:
        logger.info('"config.yaml" loaded.')
        feeds = create_feeds(feeds)
        storage.create()
        for feed in feeds:
            storage.add_feed(feed)
            check_update(feed)
        return settings


def main():
    settings = init()
    scheduler = BackgroundScheduler()
    scheduler.start()
    scheduler.add_job(
        update_feeds, trigger="interval", seconds=int(settings.get('timeout'))
    )
    return Flask(__name__)


app = main()


@app.route('/')
def index():
    feeds = storage.get_feeds()
    for feed in feeds:
        feed.image = url_for('image_folder', filename=feed.image)
    return render_template('index.html', feeds=feeds)


@app.route('/<feed_name>')
def feed_page(feed_name):
    feed = storage.get_feeds(feed_name)
    if feed is None:
        abort(404)
    sort_episodes(feed)
    return render_template('feed_page.html', feed=feed)


@app.route('/rss/<feed_name>')
def rss(feed_name):
    feed = storage.get_feeds(feed_name)
    if feed is None:
        abort(404)
    sort_episodes(feed)
    feed.image = ''.join(
            (
                request.url_root[:-1],
                url_for('image_folder', filename=feed.image),
            )
        )
    return Response(create_rss(feed), mimetype='text/xml')


@app.route('/image/<filename>')
def image_folder(filename):
    return send_from_directory('image', filename)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True)
