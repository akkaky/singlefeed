"""Parser RSS.

Parses the RSS file and returns a list of the attributes of each episode:
    'title'
    'enclosure'
    'link'
    'published'
    'description'
    'duration'
    'image'
    'author'
"""
from lxml import etree

from .date_normalize import normalize_timezone


namespaces = {
    'itunes': 'http://www.itunes.com/dtds/podcast-1.0.dtd',
    'atom': 'http://www.w3.org/2005/Atom',
}


def _parse_title(item):
    if item.find('title') is None:
        return None
    return item.find('title').text.strip()


def _parse_enclosure(item):
    if item.find('enclosure') is None:
        return None
    return dict(item.find('enclosure').attrib)


def _parse_link(item):
    if item.find('link') is None:
        return str(*item.xpath('/rss/channel/link/text()'))
    return item.find('link').text


def _parse_published(item):
    if item.find('pubDate') is None:
        return None
    return normalize_timezone(item.find('pubDate').text.strip())


def _parse_description(item):
    if item.find('description') is None:
        return None
    return item.find('description').text.strip()


def _parse_duration(item):
    if item.find('itunes:duration', namespaces) is None:
        return None
    return item.find('itunes:duration', namespaces).text


def _parse_image(item):
    if item.find('itunes:image', namespaces) is not None:
        return item.find('itunes:image', namespaces).attrib['href']
    return str(*item.xpath('/rss/channel/image/url/text()'))


def _parse_author(item):
    return str(
        *item.xpath(
            '/rss/channel/itunes:author/text()', namespaces=namespaces,
        ),
    ) or item.find('author').text


def _parse_episode(item):
    return {
        'title': _parse_title(item),
        'enclosure': _parse_enclosure(item),
        'link': _parse_link(item),
        'published': _parse_published(item),
        'description': _parse_description(item),
        'duration': _parse_duration(item),
        'image': _parse_image(item),
        'author': _parse_author(item),
    }


def get_episodes(rss_str: str) -> dict:
    feed = etree.XML(rss_str.encode('utf-8'))
    for item in feed.iter('item'):
        yield _parse_episode(item)


def get_last_build_date(rss_str: str) -> str:
    feed = etree.XML(rss_str.encode('utf-8'))
    return str(*feed.xpath('/rss/channel/lastBuildDate/text()'))