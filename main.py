import yaml
from time import sleep

from parser import create_feed
from feed import Feed
from feed import json_load


def get_settings():
    with open('settings/settings.yaml') as s:
        return yaml.load(s, Loader=yaml.BaseLoader).values()


def create_feeds(feeds):
    feeds_list = []
    for name, feed in feeds.items():
        feeds_list.append(Feed(name, *create_feed(feed)))
    return feeds_list


def create_storage(feed_list):
    for feed in feed_list:
        feed.json_dump()


def main():
    feeds, settings = get_settings()
    feeds = create_feeds(feeds)
    #feeds.append(Feed(**json_load('storage/echo-msk.json')))
    while True:
        sleep(int(settings.get('timeout')))
        for feed in feeds:
            feed.check_update()


if __name__ == '__main__':
    main()
