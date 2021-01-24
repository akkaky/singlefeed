## Singlefeed
Make your unique podcast RSS feed from several feeds and publish it. It is possible to use podcast clients.

## Install 
Make sure [Docker](https://www.docker.com/) is install on your server.

Run `git clone https://github.com/akkaky/singlefeed.git` in command line on your server.

## Config
Put images for each feed to `image` folder. 

Set up `config.yaml` in the app root directory to create your feeds.
The subblock names of the `feeds` block are using in your feed URL. 
In the `image` field of each feed enter a filename for the image, not path to file.

## Run
Execute `docker-compose up` in command line.

## Get RSS
- RSS available at `http://your_adress.com/rss/{your_feed_name}`
- RSS automatically updates when new podcast episodes are available.

## WebUI
- Access to list of episodes at: `http://your_adress.com/`
- Access to feed at: `http://your_adress.com/{your_feed_name}`
