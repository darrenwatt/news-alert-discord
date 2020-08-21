news-alert-discord
===

Scrapes BBC News homepage searching for search terms, alerts in Discord. That's it.

The following vars need to be defined in .env file
```
# database connection string for Atlas
db_string = "mongodb+srv://username:passsword@mydb.r46Gd.mongodb.net/mycluster?retryWrites=true&w=majority"

# discord webhook URL
webhook_url = "https://discordapp.com/api/webhooks/98534785628347523640575465/G76IWCyhlLxTXt75TkLBbd8RlwZ_ou7C_vn4YG9M0xns5gKQX-Lu7_cUP2BUeFJEIz"
```

And then some config stuff in config.ini
```
[general]
notify = True # set False to turn off discord notifications
loop_timer = 301 # how may seconds to re-run the fun

# change this if you want a specific section
news_url = https://www.bbc.co.uk/news/

# from bbc site, datawidths = "[240,380,420,490,573,743,820]", pick one
imgwidth = 420

searchterms = ["brexit","election"]

# discord notification
content = "This is news!"
username = "Mainstream News Bot"

# database name, defaults to "stories"
database_name = stories
```

Docker Image
====

https://cloud.docker.com/repository/docker/darrenwatt/news-alert-discord

To run locally:
```
$ docker run -it --name news-alert-discord -v "$PWD/.env:/.env" "$PWD/config.ini:/config.ini" darrenwatt/news-alert-discord:latest
```
To run from docker-compose, in your docker-compose.yml
```
services:

  news-alert-discord:

    image: darrenwatt/news-alert-discord:latest

    container_name: news-alert-discord

    volumes:

     - ${USERDIR}/docker/news-alert-discord/.env:/.env
     - ${USERDIR}/docker/news-alert-discord/config.ini:/config.ini
```
Then run with:
```
$ docker-compose -f ~/docker/docker-compose.yml up -d
```

