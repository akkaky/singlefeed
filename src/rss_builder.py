from lxml import etree

from .container import Feed
from .date_normalize import datetime_to_string
from .parser import namespaces


def create_rss(feed: Feed, url_for_feed_image: str) -> bytes:
    rss = etree.Element(
        'rss',
        nsmap={
            'atom': namespaces['atom'],
            'itunes': namespaces['itunes'],
        }
    )
    channel = etree.SubElement(rss, 'channel')
    feed_title = etree.SubElement(channel, 'title')
    feed_title.text = feed.title
    link = etree.SubElement(channel, 'link')
    link.text = feed.link
    explicit = etree.SubElement(
        channel, f"{{{namespaces['itunes']}}}explicit"
    )
    explicit.text = 'no'
    feed_description = etree.SubElement(channel, 'description')
    feed_description.text = feed.description
    last_build_date = etree.SubElement(channel, 'last_build_date')
    last_build_date.text = datetime_to_string(feed.last_build_date)
    itunes_image = etree.SubElement(
        channel, f"{{{namespaces['itunes']}}}image"
    )
    itunes_image.set('href', url_for_feed_image)
    author = etree.SubElement(
        channel, f"{{{namespaces['itunes']}}}author"
    )
    author.text = 'singlefeed'
    for episode in feed.episodes:
        item = etree.SubElement(channel, 'item')
        item_title = etree.SubElement(item, 'title')
        item_title.text = episode.title
        enclosure = etree.SubElement(item, 'enclosure')
        enclosure.set('length', episode.enclosure.length)
        enclosure.set('type', episode.enclosure.type)
        enclosure.set('url', episode.enclosure.url)
        if episode.link:
            link = etree.SubElement(item, 'link')
            link.text = episode.link
        guid = etree.SubElement(item, 'guid')
        guid.text = episode.link
        pub_date = etree.SubElement(item, 'pubDate')
        pub_date.text = datetime_to_string(episode.published)
        item_description = etree.SubElement(item, 'description')
        item_description.text = episode.description
        if episode.duration:
            duration = etree.SubElement(
                item, f"{{{namespaces['itunes']}}}duration"
            )
            duration.text = episode.duration
        explicit = etree.SubElement(
            item, f"{{{namespaces['itunes']}}}explicit",
        )
        explicit.text = 'no'
        image = etree.SubElement(item, f"{{{namespaces['itunes']}}}image")
        image.set('href', episode.image)
        author = etree.SubElement(item, 'author')
        author.text = episode.author
    return etree.tostring(
        rss, xml_declaration=True, encoding='utf-8', method="xml",
        pretty_print=True
    )
