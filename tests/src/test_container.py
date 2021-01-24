from unittest import TestCase

from src.container import Episode, Feed, get_container_attrs_keys


episode = Episode(
                    title='Title 1',
                    enclosure={
                        'length': '26229027',
                        'type': 'audio/mpeg',
                        'url': 'https://example.com/1.mp3'
                    },
                    link='https://example.com/episode',
                    published='Thu, 24 Dec 2020 22:58:27 +0000',
                    description='Item description',
                    duration='27:20',
                    image='https://example.com/_3000px.jpg',
                    author="Feed's author",
                    )
feed = Feed(
            name='Feed name',
            title='Feed title',
            link='Feed link',
            language='language',
            description='Feed description',
            image='Feed image',
            sources='source1, source2',
            last_build_date='Thu, 24 Dec 2022 22:58:27 +0000',
            episodes=[episode],
        )


class EpisodeTestCase(TestCase):

    def test__get_attrs_values(self):
        expected_result = [
            'Title 1',
            '26229027, audio/mpeg, https://example.com/1.mp3',
            'https://example.com/episode',
            'Thu, 24 Dec 2020 22:58:27 +0000',
            'Item description',
            '27:20',
            'https://example.com/_3000px.jpg',
            "Feed's author",
        ]
        self.assertListEqual(expected_result, list(episode.get_attrs_values()))


class FeedTestCase(TestCase):

    def test__get_attrs_values(self):
        expected_tesult = [
            'Feed name',
            'Feed title',
            'Feed link',
            'language',
            'Feed description',
            'Feed image',
            'source1, source2',
            'Thu, 24 Dec 2022 22:58:27 +0000',
        ]
        self.assertListEqual(expected_tesult, list(feed.get_attrs_values()))


class GetContainerAttrsKeysTestCase(TestCase):

    def test__feed_class(self):
        expected_data = (
            'name, title, link, language, description, image, sources, '
            'last_build_date'
        )
        self.assertEqual(expected_data, get_container_attrs_keys('Feed'))

    def test__episode_class(self):
        expected_data = (
            'feed_name, title, enclosure, link, published, description, '
            'duration, image, author'
        )
        self.assertEqual(expected_data, get_container_attrs_keys('Episode'))
