import os, json
from dotenv import load_dotenv

load_dotenv()

class Config(object):
    LOG_FORMAT = os.getenv("LOG_FORMAT") or '%(asctime)s - %(levelname)s - %(message)s \t - %(name)s (%(filename)s).%(funcName)s(%(lineno)d) ' # https://docs.python.org/3/howto/logging.html#changing-the-format-of-displayed-messages
    LOG_LEVEL = os.getenv("LOG_LEVEL") or 'INFO'
    APPNAME = os.getenv("APPNAME") or 'NONE'
    ENV = os.getenv("ENV") or "DEV"
    REPEAT_DELAY = os.getenv("REPEAT_DELAY") or 300

    SOURCE_URL = os.getenv("SOURCE_URL") or "https://www.bbc.co.uk/news"
    IMGWIDTH = os.getenv("IMGWIDTH") or 420 # from bbc site, datawidths = "[240,380,420,490,573,743,820]", pick one
    KEYWORDS =  os.getenv("KEYWORDS") or "Boris" # supply as string with spaces
    SEARCHSPECIFIC = os.getenv("SEARCHSPECIFIC") or 'False'

    # Discord - off by default
    DISCORD_NOTIFY = os.getenv("DISCORD_NOTIFY") or 'False'
    DISCORD_CONTENT = os.getenv("DISCORD_CONTENT") or "Mainstream News!"
    DISCORD_USERNAME = os.getenv("DISCORD_USERNAME") or "News Bot"
    DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL") or "None"
    MONGO_DBSTRING = os.getenv("MONGO_DBSTRING") or "None"
    MONGO_DB = os.getenv("MONGO_DB") or "mongo001"
    MONGO_COLLECTION = os.getenv("MONGO_COLLECTION") or "mongo_test_collection"

    # Twitter - off by default
    TWITTER_NOTIFY = os.getenv("TWITTER_NOTIFY") or 'False'
    TWITTER_STATUS_PREFIX = os.getenv("TWITTER_STATUS_PREFIX") or "None"
    TWITTER_CONSUMER_KEY = os.getenv("TWITTER_CONSUMER_KEY") or 'False'
    TWITTER_CONSUMER_SECRET = os.getenv("TWITTER_CONSUMER_SECRET") or 'False'
    TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN") or 'False'
    TWITTER_ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET") or 'False'
