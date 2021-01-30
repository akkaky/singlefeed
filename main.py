import logging
import yaml
import requests
import sys
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from flask import (
    abort, Flask, Response, render_template, request, send_from_directory,
    url_for,
)

from src import parser
from src.container import Episode, Feed
from src.date_normalize import string_to_datetime, datetime_to_string
from src.rss_builder import create_rss
from src import storage


default_settings = {'timeout': '60'}
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s',
)
logger = logging.getLogger(__name__)


def get_config() -> dict:
    try:
        with open('config.yaml') as s:
            return yaml.load(s, Loader=yaml.BaseLoader)
    except FileNotFoundError as e:
        logger.error(e)
        sys.exit()


def create_feeds(feeds: dict) -> list[Feed]:
    feeds_list = []
    for name, feed in feeds.items():
        feed = Feed(
            name=name,
            title=feed.get('title'),
            link=feed.get('link'),
            language=feed.get('language'),
            description=feed.get('description'),
            image=feed.get('image'),
            sources=feed.get('sources'),
        )
        if feed:
            logger.info(f'"{feed.name}" feed created.')
        else:
            logger.error(f"Can't to create {name} feed")
        feeds_list.append(feed)
    return feeds_list


def sort_episodes(feed: Feed):
    if feed.last_build_date:
        feed.episodes.sort(
            key=lambda episode: string_to_datetime(episode.published),
            reverse=True,
        )


def add_new_episodes(feed: Feed, rss_: str) -> list[Episode]:
    episodes = (Episode(**episode) for episode in parser.get_episodes(rss_))
    return [episode for episode in episodes if episode not in feed.episodes]


def check_update(feed: Feed):
    new_episodes = []
    logger.info(f'"{feed.name}" check updates...')
    for url in feed.sources:
        rss_str = requests.get(url).text
        new_episodes.extend(add_new_episodes(feed, rss_str))
    if new_episodes:
        logger.info(f'"{feed.name}" {len(new_episodes)} new episodes added.')
        feed.last_build_date = datetime_to_string(datetime.now().astimezone())
        storage.add_episodes(feed.name, new_episodes)
        storage.update_last_build_date(feed)
    else:
        logger.info(f'"{feed.name}" feed is up to date.')


def update_feeds():
    for feed in storage.get_feeds():
        check_update(feed)


def init() -> dict:
    config = get_config()
    try:
        feeds = config['feeds']
        logger.info('"config.yaml" loaded.')
    except KeyError as e:
        logger.error(f'"config.yaml" is incorrect. Fill block {e} correctly.')
        sys.exit()
    settings = config.setdefault('settings', default_settings)
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
        update_feeds, trigger="interval", seconds=int(settings['timeout'])
    )
    return Flask(__name__)


app = main()


def load_feed_from_db(feed_name):
    feed = storage.get_feeds(feed_name)
    if feed is None:
        abort(404)
    try:
        sort_episodes(feed)
    except TypeError as e:
        logger.error(e)
    finally:
        return feed


@app.route('/')
def index():
    feeds = storage.get_feeds()
    for feed in feeds:
        feed.image = url_for('image_folder', filename=feed.image)
    return render_template('index.html', feeds=feeds)


@app.route('/<feed_name>')
def feed_page(feed_name):
    feed = load_feed_from_db(feed_name)
    return render_template('feed_page.html', feed=feed)


@app.route('/rss/<feed_name>')
def rss(feed_name):
    feed = load_feed_from_db(feed_name)
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
