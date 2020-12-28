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


@dataclass
class Feed:
    name: str
    title: str
    link: str
    language: str
    description: str
    image: str
    sources: list[str] = field(default_factory=list)
    last_build_date: str = None
    episodes: list[Episode] = field(default_factory=list)


class FeedEpisodeEncoder(JSONEncoder):

    def default(self, obj: Union[Feed, Episode]) -> dict:
        if isinstance(obj, (Feed, Episode)):
            return obj.__dict__
        return JSONEncoder.default(self, obj)
