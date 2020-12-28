import json

from .feed import Feed, FeedEpisodeEncoder


def json_load(file_name: str) -> dict:
    with open(file_name) as json_file:
        return json.load(json_file)


def json_dump(feed: Feed):
    with open(f'{feed.name}.json', 'w') as file:
        json.dump(feed, file, cls=FeedEpisodeEncoder, indent=4)
        print(f'"{feed.name}.json" file created')
