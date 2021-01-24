import logging

from sqlalchemy import Column, DateTime, ForeignKey, Integer, MetaData, \
    String, Table, create_engine
from sqlalchemy.orm import Session, registry, relationship

from .container import Episode, Enclosure, Feed, Source


logger = logging.getLogger(__name__)
db_file = 'singlefeed.sqlite'
engine = create_engine(f'sqlite:///{db_file}')
session = Session(engine)
mapper_registry = registry()
metadata = MetaData(engine)
enclosure_table = Table(
    'enclosure',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('episode_id', Integer, ForeignKey('episodes.id')),
    Column('length', String),
    Column('type', String),
    Column('url', String),
)
episodes_table = Table(
    'episodes',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('feed_name', String, ForeignKey('feeds.name')),
    Column('title', String),
    Column('link', String),
    Column('published', DateTime),
    Column('description', String),
    Column('duration', String),
    Column('image', String),
    Column('author', String)
)
sources_table = Table(
    'sources',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('feed_name', String, ForeignKey('feeds.name')),
    Column('url', String),
)
feeds_table = Table(
    'feeds',
    metadata,
    Column('name', String, primary_key=True),
    Column('title', String),
    Column('link', String),
    Column('language', String),
    Column('description', String),
    Column('image', String),
    Column('last_build_date', DateTime)

)
mapper_registry.map_imperatively(
    Feed, feeds_table, properties={
        'sources': relationship(Source),
        'episodes': relationship(Episode, order_by='Episode.published.desc()')
    }
)

mapper_registry.map_imperatively(
    Episode, episodes_table, properties={
        'enclosure': relationship(Enclosure, uselist=False)
    }
)
mapper_registry.map_imperatively(Enclosure, enclosure_table)
mapper_registry.map_imperatively(Source, sources_table)
metadata.drop_all()
metadata.create_all()
