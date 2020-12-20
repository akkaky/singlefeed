import json
from datetime import datetime
from dataclasses import dataclass
from operator import attrgetter


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
    episodes: list
    last_build_date: datetime = None

    def __post_init__(self):
        self.episodes = [Episode(**episode) for episode in self.episodes]
        self.sort_episodes()
        self.last_build_date = self.episodes[0].published

    def as_dict(self):
        return {
            'name': self.name,
            'title': self.title,
            'link': self.link,
            'language': self.language,
            'description': self.description,
            'image': self.description,
            'last_build_date': self.last_build_date.strftime(
                '%a, %d %b %Y %H:%M:%S %z',
            ),
            'episodes': [episode.as_dict() for episode in self.episodes]}

    def json_dump(self):
        with open(f'storage/{self.name}.json', 'w') as file:
            json.dump(self.as_dict(), file, indent=4)

    def sort_episodes(self):
        self.episodes.sort(key=attrgetter('published'), reverse=True)

    @staticmethod
    def json_load(file_name):
        with open(file_name) as json_file:
            feed = json.load(json_file)
        return Feed(**feed)
