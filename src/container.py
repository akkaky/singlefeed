from dataclasses import dataclass, field
from json import JSONEncoder
from typing import Union


@dataclass
class Episode:
    title: str
    enclosure: dict
    link: str
    published: str
    description: str
    duration: str
    image: str
    author: str

    def get_attrs_values(self):
        return (
            ', '.join(self.enclosure.values()) if attr == 'enclosure'
            else self.__getattribute__(attr) for attr in self.__dict__
        )


@dataclass
class Feed:
    name: str
    title: str
    link: str
    language: str
    description: str
    image: str
    sources: str
    last_build_date: str = None
    episodes: list[Episode] = field(default_factory=list)

    def get_attrs_values(self):
        return (
            self.__getattribute__(attr) for attr in self.__dict__
            if attr != 'episodes'
        )


class FeedEpisodeJsonEncoder(JSONEncoder):

    def default(self, obj: Union[Feed, Episode]) -> dict:
        if isinstance(obj, (Feed, Episode)):
            return obj.__dict__
        return JSONEncoder.default(self, obj)


def create_episode(data):
    name, enclosure, *data = data
    length, type_, url = enclosure.split(', ')
    enclosure = {'length': length, 'type': type_, 'url': url}
    return Episode(name, enclosure, *data)
