import yaml

from parser import parse_feed
from feed import Feed
from builder import create_rss


def get_settings():
    with open('settings/settings.yaml') as s:
        return yaml.load(s, Loader=yaml.BaseLoader)


def get_feed_list(feeds):
    feeds_list = []
    for name, feed in feeds.items():
        feeds_list.append(Feed(name, *parse_feed(feed)))
    return feeds_list


def create_storage(feed_list):
    for feed in feed_list:
        feed.json_dump()


def main():
    settings = get_settings()
    feed_list = get_feed_list(settings['feeds'])
    create_storage(feed_list)
    for feed in feed_list:
        create_rss(feed)


if __name__ == '__main__':
    main()
