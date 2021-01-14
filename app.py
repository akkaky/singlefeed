from flask import Flask, Response, render_template

from main import main, sort_episodes
from src import storage
from src.rss_builder import create_rss

app = Flask(__name__)


@app.route('/')
def index():
    feeds = storage.get_feeds()
    return render_template('index.html', feeds=feeds)


@app.route('/<feed_name>')
def feed_page(feed_name):
    feed = storage.get_feeds(feed_name)
    sort_episodes(feed)
    return render_template('feed_page.html', feed=feed)


@app.route('/rss/<feed_name>')
def rss(feed_name):
    feed = storage.get_feeds(feed_name)
    sort_episodes(feed)
    return Response(create_rss(feed), mimetype='text/xml')


main()


if __name__ == '__main__':
    app.run()

