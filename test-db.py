from pymongo import MongoClient
import logging
from config import Config

Config = Config()
logging.basicConfig(format=Config.LOG_FORMAT ,level=Config.LOG_LEVEL)

logging.info("Setting up connection to mongodb at: "+Config.MONGO_DBSTRING)
mongoclient = MongoClient(Config.MONGO_DBSTRING)
db = mongoclient[Config.MONGO_DB]
collection = db[Config.MONGO_COLLECTION]
logging.info("Database is: " + Config.MONGO_DB)
logging.info("Collection is: " + Config.MONGO_COLLECTION)

mydict = { "name": "Tim", "address": "23 Meteor Street" }

x = collection.insert_one(mydict)
print(x.inserted_id)