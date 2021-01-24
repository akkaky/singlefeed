from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Enclosure:

    id: int = field(init=False)
    length: str
    type: str
    url: str


@dataclass
class Episode:

    id: int = field(init=False)
    title: str
    enclosure: Enclosure
    link: str
    published: datetime
    description: str
    duration: str
    image: str
    author: str


@dataclass
class Source:

    id: int = field(init=False)
    url: str


@dataclass
class Feed:

    name: str
    title: str
    link: str
    language: str
    description: str
    image: str
    last_build_date: datetime = None
    sources: list[Source] = field(default_factory=list)
    episodes: list[Episode] = field(default_factory=list)
