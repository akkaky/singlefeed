"""Parser RSS.

Parse XML, return a list of episodes with needed tags.
"""
from lxml import etree

namespaces = {
    'itunes': 'http://www.itunes.com/dtds/podcast-1.0.dtd',
    'atom': 'http://www.w3.org/2005/Atom',
}


class ParserFeed:
    def __init__(self, *content):
        self.feeds = list()
        for req in content:
            self.feeds.extend(self._get_items(etree.XML(req.encode('utf-8'))))

    @staticmethod
    def _get_item(item, image, author):
        return {
            'title': item.find('title').text.strip(),
            'enclosure': item.find('enclosure').attrib,
            'link': item.find('link').text,
            'published': item.find('pubDate').text,
            'description': item.find('description').text.strip(),
            'duration': item.find('itunes:duration', namespaces).text,
            'image': image,
            'author': author or item.find('author').text,
        }

    def _get_items(self, feed):
        self.image = str(*feed.xpath('//channel/image/url/text()'))
        self.author = str(
            *feed.xpath(
                '//channel/itunes:author/text()', namespaces=namespaces,
            )
        )
        return [
            self._get_item(item, self.image, self.author) for item in
            feed.iter('item')
        ]

    def get_feeds_dict(self):
        """
        This method just for test now
        """
        return self.feeds
