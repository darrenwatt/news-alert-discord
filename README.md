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
```

Running in Heroku notes:
```
git push heroku master
heroku ps:scale worker=1
heroku logs --tail
```