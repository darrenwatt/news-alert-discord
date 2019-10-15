Deathscraper
===

Scrapes BBC News homepage searching for death, alerts in Discord. That's it.

Running in Heroku notes:

```
git push heroku master
heroku ps:scale worker=1
heroku logs --tail
```