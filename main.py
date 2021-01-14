import yaml
import requests

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, Response, render_template
from flask_script import Manager, Server, Command, Option
from gunicorn.app.base import Application

from src import parser
from src.container import Episode, Feed
from src.date_normalize import (
    normalize_timezone, string_to_datetime,
    datetime_to_string,
)
from src.rss_builder import create_rss
from src import storage


def get_config() -> dict:
    with open('config.yaml') as s:
        return yaml.load(s, Loader=yaml.BaseLoader).values()


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
            print(f'"{feed.name}" feed created.')
        else:
            print(f"Can't to create {name} feed")
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
    print(f'"{feed.name}" check updates...')
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
        print(f'"{feed.name}" {len(new_episodes)} new episodes added.')
        feed.last_build_date = datetime_to_string(max(last_build_date_list))
        storage.add_episodes(feed.name, new_episodes)
        storage.update_last_build_date(feed)
    else:
        print(f'"{feed.name}" feed is up to date.')


def update_feeds():
    for feed in storage.get_feeds():
        check_update(feed)


def init():
    feeds, settings = get_config()
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
