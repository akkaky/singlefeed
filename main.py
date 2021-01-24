import logging
import yaml
import requests
import sys
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, Response, abort, render_template, request, \
    send_from_directory, url_for
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from src import parser
from src.container import Enclosure, Episode, Feed, Source
from src.date_normalize import string_to_datetime
from src.rss_builder import create_rss
from src.storage import engine


default_settings = {'timeout': '60'}
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s',
)
logger = logging.getLogger(__name__)
session = Session(engine)


def get_config() -> dict:
    try:
        with open('config.yaml') as s:
            return yaml.load(s, Loader=yaml.BaseLoader)
    except FileNotFoundError as e:
        logger.error(e)
        sys.exit()


def create_feeds(feeds: dict) -> list[Feed]:
    feeds_list = []
    for name, feed_data in feeds.items():
        feed = Feed(
            name=name,
            title=feed_data.get('title'),
            link=feed_data.get('link'),
            language=feed_data.get('language'),
            description=feed_data.get('description'),
            image=feed_data.get('image'),
            sources=[Source(url) for url in feed_data.get('sources')],
        )
        if feed_data:
            logger.info(f'"{feed.name}" feed_data created.')
        else:
            logger.error(f"Can't to create {name} feed_data")
        feeds_list.append(feed)
    return feeds_list


def sort_episodes(feed: Feed):
    if feed.last_build_date:
        feed.episodes.sort(
            key=lambda episode: string_to_datetime(episode.published),
            reverse=True,
        )


def new_episodes_list(feed: Feed, rss_: str) -> list[Episode]:
    episodes = (
        Episode(
            title=episode['title'],
            enclosure=Enclosure(**episode['enclosure']),
            link=episode['link'],
            published=string_to_datetime(episode['published']),
            description=episode['description'],
            duration=episode['duration'],
            image=episode['image'],
            author=episode['author'],
        ) for episode in parser.get_episodes(rss_)
    )
    return [
        episode for episode in episodes if (episode.title, episode.link) not in
        [(e.title, e.link) for e in feed.episodes]
    ]


def check_update(feed: Feed):
    new_episodes = []
    logger.info(f'"{feed.name}" check updates...')
    for source in feed.sources:
        rss_str = requests.get(source.url).text
        new_episodes.extend(new_episodes_list(feed, rss_str))
    if new_episodes:
        feed.episodes.extend(new_episodes)
        feed.last_build_date = datetime.now().astimezone()
        logger.info(f'"{feed.name}" {len(new_episodes)} new episodes added.')
    else:
        logger.info(f'"{feed.name}" feed is up to date.')


def update_feeds():
    for feed in session.query(Feed).all():
        check_update(feed)
        session.commit()


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
    for feed in feeds:
        session.add(feed)
    session.commit()
    return settings


def main():
    settings = init()
    update_feeds()
    scheduler = BackgroundScheduler()
    scheduler.start()
    scheduler.add_job(
        update_feeds, trigger="interval", seconds=int(settings['timeout'])
    )
    return Flask(__name__)


app = main()


def load_feed_from_db(feed_name: str) -> Feed:
    try:
        return session.query(Feed).filter_by(name=feed_name).one()
    except TypeError as e:
        logger.error(e)
        abort(404)


@app.route('/')
def index():
    feeds = session.query(Feed).all()
    return render_template('index.html', feeds=feeds)


@app.route('/<feed_name>')
def feed_page(feed_name):
    try:
        feed = load_feed_from_db(feed_name)
        return render_template('feed_page.html', feed=feed)
    except NoResultFound:
        abort(404)


@app.route('/rss/<feed_name>')
def rss(feed_name):
    feed = load_feed_from_db(feed_name)
    url_for_feed_image: str = ''.join(
            (
                request.url_root[:-1],
                url_for('image_folder', filename=feed.image),
            ),
        )
    print(url_for_feed_image)
    return Response(create_rss(feed, url_for_feed_image), mimetype='text/xml')


@app.route('/image/<filename>')
def image_folder(filename):
    return send_from_directory('image', filename)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True)
