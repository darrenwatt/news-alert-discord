Deathscraper
===

Scrapes BBC News homepage searching for death, alerts in Discord. That's it.

The following vars need to be defined in .env file
```
db_name = ""
db_host = ""
db_port = integer
db_user = ""
db_pass = ""

#discord stuff
webhook_url = ""

notify = True/False (default True)
loop_timer = integer (default 300)
news_url = "https://www.bbc.co.uk/news/entertainment_and_arts" (default https://www.bbc.co.uk/news)
```

Docker Image
====

https://cloud.docker.com/repository/docker/darrenwatt/deathscraper

To run locally:
```
$ docker run -it --name deathscraper -v "$PWD/.env:/.env" darren/deathscraper
```
To run from docker-compose, in your docker-compose.yml
```
services:

  deathscraper:

    image: darrenwatt/deathscraper:latest

    container_name: deathscraper

    volumes:

     - ${USERDIR}/docker/deathscraper/.env:/.env
```
Then run with:
```
$ docker-compose -f ~/docker/docker-compose.yml up -d
```

Running in Heroku notes (untested:
```
git push heroku master
heroku ps:scale worker=1
heroku logs --tail
```
