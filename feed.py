import json
from typing import List
from datetime import datetime
from dataclasses import dataclass, field
from operator import attrgetter

from parser import get_episodes
from parser import get_last_build_date
from builder import create_rss


@dataclass
class Episode:
    title: str
    enclosure: dict
    link: str
    published: datetime
    description: str
    duration: str
    image: str
    author: str

    def __post_init__(self):
        if isinstance(self.published, str):
            self.published = datetime.strptime(
                self.published, '%a, %d %b %Y %H:%M:%S %z',
            )

    def as_dict(self):
        return {
            'title': self.title,
            'enclosure': self.enclosure,
            'link': self.link,
            'published': self.published.strftime('%a, %d %b %Y %H:%M:%S %z'),
            'description': self.description,
            'duration': self.duration,
            'image': self.image,
            'author': self.author
        }


@dataclass
class Feed:
    name: str
    title: str
    link: str
    language: str
    description: str
    image: str
    sources: List[str] = field(default_factory=list)
    last_build_date: datetime = None
    episodes: List[Episode] = field(default_factory=list)

    def __post_init__(self):
        print(f'"{self.name}" feed creating...')
        if self.episodes:
            self.episodes = [Episode(**episode) for episode in self.episodes]
            if isinstance(self.last_build_date, str):
                self.last_build_date = datetime.strptime(
                    self.last_build_date, '%a, %d %b %Y %H:%M:%S %z',
                )
        self.check_update()
        create_rss(self)
        print(f'"{self.name}_rss.xml" created.')
        print(f'"{self.name}" feed created.')

    def as_dict(self):
        return {
            'name': self.name,
            'title': self.title,
            'link': self.link,
            'language': self.language,
            'description': self.description,
            'image': self.description,
            'sources': self.sources,
            'last_build_date': self.last_build_date.strftime(
                '%a, %d %b %Y %H:%M:%S %z',
            ),
            'episodes': [episode.as_dict() for episode in self.episodes],
        }

    def json_dump(self):
        with open(f'storage/{self.name}.json', 'w') as file:
            json.dump(self.as_dict(), file, indent=4)
        print(f'"{self.name}.json" file created')

    def sort_episodes(self):
        self.episodes.sort(key=attrgetter('published'), reverse=True)

    def add_episode(self, url):
        counter = 0
        for episode in get_episodes(url):
            episode = Episode(**episode)
            if episode in self.episodes:
                break
            self.episodes.append(episode)
            counter += 1
        return counter

    def check_update(self):
        counter = 0
        has_update = False
        last_build_date_list = []
        print(f'"{self.name}" check updates...')
        for url in self.sources:
            last_build_date_list.append(get_last_build_date(url))
            if (
                self.last_build_date is None or (
                    self.last_build_date < max(last_build_date_list)
                )
            ):
                has_update = True
                counter += self.add_episode(url)
        if has_update:
            print(f'{counter} new episodes added.')
            self.last_build_date = max(last_build_date_list)
            self.sort_episodes()
            self.json_dump()
            create_rss(self)
            print(f'"{self.name}_rss.xml" created.')
        print(f'"{self.name}" feed is up to date.')


def json_load(file_name):
    with open(file_name) as json_file:
        feed = json.load(json_file)
    return feed
