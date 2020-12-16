"""Parser RSS.

Parse XML, return a list of series with the required tags.
"""
from datetime import datetime
from operator import itemgetter
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
        self.feeds.sort(key=itemgetter('published'), reverse=True),
        self.rss = None

    @staticmethod
    def _get_date_obj(date_string):
        return datetime.strptime(date_string, '%a, %d %b %Y %H:%M:%S %z')

    @staticmethod
    def _get_item(item, image, author):
        return {
            'title': item.find('title').text.strip(),
            'enclosure': item.find('enclosure').attrib,
            'link': item.find('link').text,
            'published': ParserFeed._get_date_obj(
                item.find('pubDate').text.strip()
            ),
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

    def get_rss(self, title='Your fees name', description='Your description'):
        """!!!should be separated into functions!!!"""
        rss = etree.Element('rss', nsmap={'itunes': namespaces['itunes']})
        channel = etree.SubElement(rss, 'channel')
        feed_title = etree.SubElement(channel, 'title')
        feed_title.text = title
        explicit = etree.SubElement(
            channel, f"{{{namespaces['itunes']}}}explicit"
        )
        explicit.text = 'no'
        feed_description = etree.SubElement(channel, 'description')
        feed_description.text = description
        for episode in self.feeds:
            item = etree.SubElement(channel, 'item')
            item_title = etree.SubElement(item, 'title')
            item_title.text = episode['title']
            enclosure = etree.SubElement(item, 'enclosure')
            for key, value in episode['enclosure'].items():
                enclosure.set(key, value)
            duration = etree.SubElement(
                item, f"{{{namespaces['itunes']}}}duration"
            )
            explicit = etree.SubElement(
                item, f"{{{namespaces['itunes']}}}explicit",
            )
            explicit.text = 'no'
            duration.text = episode['duration']
            link = etree.SubElement(item, 'link')
            link.text = episode['link']
            guid = etree.SubElement(item, 'guid')
            guid.text = episode['link']
            item_description = etree.SubElement(item, 'description')
            item_description.text = episode['description']
            pub_date = etree.SubElement(item, 'pubDate')
            pub_date.text = datetime.strftime(
                episode['published'], '%a, %d %b %Y %H:%M:%S %z'
            )
            image = etree.SubElement(item, 'image')
            image.text = episode['image']
            author = etree.SubElement(item, 'author')
            author.text = episode['author']
        tree = etree.ElementTree(rss)
        tree.write(
            'rss.xml', xml_declaration=True, encoding='utf-8', method="xml",
            pretty_print=True,
        )
