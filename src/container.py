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
    last_build_date: str = None
    sources: list = field(default_factory=list)
    episodes: list[Episode] = field(default_factory=list)

    def get_attrs_values(self):
        return (
            self.__getattribute__(attr) for attr in self.__dict__
            if attr not in ('sources', 'episodes')
        )


def get_container_attrs_keys(dataclass_name: str) -> str:
    if dataclass_name == 'Feed':
        return ', '.join(list(Feed.__dict__['__dataclass_fields__'])[:-2])
    if dataclass_name == 'Episode':
        return (
            f'feed_name, {", ".join(Episode.__dict__["__dataclass_fields__"])}'
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
