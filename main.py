import requests
from parser import ParserFeed


def main():
    urls = [
        'http://zemlekop.libsyn.com/rss',
        'http://echo.msk.ru/programs/personalno/rss-audio.xml',
    ]
    req = [requests.get(url).text for url in urls]
    feeds = ParserFeed(*req)
    for num, item in enumerate(feeds.get_feeds_dict(), 1):
        print(f'Episode {num}')
        for key, value in item.items():
            print(f'{key} :: {value}')


if __name__ == '__main__':
    main()
