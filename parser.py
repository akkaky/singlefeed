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
import requests
from datetime import datetime
from lxml import etree

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


def _normalize_published(published):
    time_zones = {
        'EST': '-0500',
        'PDT': '-0700',
        'PST': '-0800',
    }
    time_zone = published.rsplit(' ', 1)[-1]
    if time_zone in time_zones:
        return published.replace(time_zone, time_zones[time_zone])
    return published


def _get_date_obj(item):
    if item.find('pubDate') is None:
        return None
    published = _normalize_published(item.find('pubDate').text.strip())
    return datetime.strptime(published, '%a, %d %b %Y %H:%M:%S %z')


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
        'published': _get_date_obj(item),
        'description': _parse_description(item),
        'duration': _parse_duration(item),
        'image': _parse_image(item),
        'author': _parse_author(item),
    }


def get_episodes(url):
    feed = etree.XML(requests.get(url).text.encode('utf-8'))
    for item in feed.iter('item'):
        yield _parse_episode(item)


def create_feed(feed):
    title = feed.get('title')
    link = feed.get('link')
    language = feed.get('language')
    description = feed.get('description')
    image = feed.get('image')
    sources = feed.get('sources')
    return title, link, language, description, image, sources


def get_last_build_date(url):
    feed = etree.XML(requests.get(url).text.encode('utf-8'))
    last_build_date = _normalize_published(
        str(*feed.xpath('/rss/channel/lastBuildDate/text()'))
    )
    return datetime.strptime(last_build_date, '%a, %d %b %Y %H:%M:%S %z')
