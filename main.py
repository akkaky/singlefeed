import os.path
import yaml
import requests
from time import sleep

from src.parser import get_last_build_date, get_episodes
from src.feed import Episode, Feed
from src.storage import json_load, json_dump
from src.date_normalize import string_to_datetime
from src.rss_builder import create_rss


def get_config() -> dict:
    with open('config.yaml') as s:
        return yaml.load(s, Loader=yaml.BaseLoader).values()


def get_feed_attributes(feed: dict) -> tuple:
    title = feed.get('title')
    link = feed.get('link')
    language = feed.get('language')
    description = feed.get('description')
    image = feed.get('image')
    sources = feed.get('sources')
    return title, link, language, description, image, sources


def create_feeds(feeds: dict) -> list:
    feeds_list = []
    for name, feed in feeds.items():
        feed = Feed(name, *get_feed_attributes(feed))
        if feed:
            print(f'"{feed.name}" feed created.')
        else:
            print(f"Can't to create {name} feed")
        feeds_list.append(feed)
    return feeds_list


def sort_episodes(feed: Feed):
    feed.episodes.sort(
        key=lambda episode: string_to_datetime(episode.published), reverse=True
    )


def add_episodes(feed: Feed, rss: str) -> int:
    counter = 0
    for episode in get_episodes(rss):
        episode = Episode(**episode)
        if episode in feed.episodes:
            break
        feed.episodes.append(episode)
        counter += 1
    return counter


def check_update(feed: Feed) -> bool:
    counter = 0
    has_update = False
    last_build_date_list = []
    print(f'"{feed.name}" check updates...')
    for url in feed.sources:
        rss_str = requests.get(url).text
        last_build_date_list.append(get_last_build_date(rss_str))
        if (
            feed.last_build_date is None or (
                feed.last_build_date < max(
                    last_build_date_list, key=string_to_datetime
                )
            )
        ):
            has_update = True
            counter += add_episodes(feed, rss_str)
    if has_update:
        print(f'"{feed.name}" {counter} new episodes added.')
        feed.last_build_date = max(
            last_build_date_list, key=string_to_datetime
        )
        sort_episodes(feed)
    print(f'"{feed.name}" feed is up to date.')
    return has_update


def main():
    feeds, settings = get_config()
    feeds = create_feeds(feeds)
    for feed in feeds:
        json_file_name = f'{feed.name}.json'
        if os.path.isfile(json_file_name):
            json_data = json_load(json_file_name)
            feed.episodes = [
                Episode(**episode) for episode in json_data['episodes']
            ]
            print(
                f'"{feed.name}" {len(feed.episodes)} '
                'episodes loaded from database.'
            )
    while True:
        for feed in feeds:
            if check_update(feed):
                json_dump(feed)
                with open(f'{feed.name}_rss.xml', 'wb') as file:
                    file.write(create_rss(feed))

        sleep(int(settings['timeout']))


if __name__ == '__main__':
    main()
