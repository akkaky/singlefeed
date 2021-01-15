from flask import url_for
from lxml import etree

from .parser import namespaces


def get_url(srt):
    pass

def create_rss(feed):
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
    last_build_date.text = feed.last_build_date
    image = etree.SubElement(channel, 'image')
    url = etree.SubElement(image, 'url')
    url.text = feed.image
    itunes_image = etree.SubElement(
        channel, f"{{{namespaces['itunes']}}}image"
    )
    itunes_image.set('href', feed.image)
    author = etree.SubElement(
        channel, f"{{{namespaces['itunes']}}}author"
    )
    author.text = 'test'
    for episode in feed.episodes:
        item = etree.SubElement(channel, 'item')
        item_title = etree.SubElement(item, 'title')
        item_title.text = episode.title
        enclosure = etree.SubElement(item, 'enclosure')
        for key, value in episode.enclosure.items():
            enclosure.set(key, value)
        if episode.link:
            link = etree.SubElement(item, 'link')
            link.text = episode.link
        guid = etree.SubElement(item, 'guid')
        guid.text = episode.link
        pub_date = etree.SubElement(item, 'pubDate')
        pub_date.text = episode.published
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
