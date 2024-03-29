from ast import keyword
from config import Config
from pymongo import MongoClient
from bs4 import BeautifulSoup
import requests, time, json, re, tweepy, logging

Config = Config()
logging.basicConfig(format=Config.LOG_FORMAT ,level=Config.LOG_LEVEL)
logging.info("Yoyoyo, starting up in the house!")

logging.info("Setting up connection to mongodb at: "+Config.MONGO_DBSTRING)
mongoclient = MongoClient(Config.MONGO_DBSTRING)
db = mongoclient[Config.MONGO_DB]
collection = db[Config.MONGO_COLLECTION]
logging.info("Database is: " + Config.MONGO_DB)
logging.info("Collection is: " + Config.MONGO_COLLECTION)

# string to list
keywords=Config.KEYWORDS.split()

if Config.SEARCHSPECIFIC == 'True':
    # match exact terms only
    reg = re.compile(r'(?i)\b(?:%s)\b' % '|'.join(keywords))
else:
    # match any partial term, this seems to work, I suck at regex so this might well be wrong
    reg = re.compile(r'(?i)%s' % '|'.join(keywords))

logging.info("regex output:")
logging.info(reg)


if Config.TWITTER_NOTIFY == 'True':
    logging.info("Tweeting is enabled")

    twitter_consumer_key = Config.TWITTER_CONSUMER_KEY
    twitter_consumer_secret = Config.TWITTER_CONSUMER_SECRET
    twitter_access_token = Config.TWITTER_ACCESS_TOKEN
    twitter_access_token_secret = Config.TWITTER_ACCESS_TOKEN_SECRET

    client = tweepy.Client(
    consumer_key=twitter_consumer_key, consumer_secret=twitter_consumer_secret,
    access_token=twitter_access_token, access_token_secret=twitter_access_token_secret
    )

else:
    logging.info("Tweeting is disabled")


def scrape_bbc_news():
    logging.info("Getting stories now.")
    try:
        response = requests.get(Config.SOURCE_URL)
    except requests.exceptions.RequestException as e:
        logging.info(e)
        logging.info("Failed. Never mind... we'll try again in a bit.")
        return
    doc = BeautifulSoup(response.text, 'html.parser')

    # Start with an empty list
    stories_list = []
    stories = doc.find_all('div', {'class': 'gs-c-promo'})
    for story in stories:
        # Create a dictionary without anything in it
        story_dict = {}
        headline = story.find('h3').text
        logging.info("Checking headline: " + headline)
        if reg.search(headline):
            logging.info("Match found")
            story_dict['headline'] = headline
            link = story.find('a')
            if link:
                story_dict['url'] = link['href']
            img = story.find('img')
            if img:
                logging.info(img)
                try:
                    logging.info(img['data-src'])
                except NameError:
                    logging.info("Variable data-src is not defined")
                except KeyError:
                    logging.info("probably want data instead")
                    story_dict['img'] = img['src']
                else:
                    story_dict['img'] = img['data-src'].replace("{width}", Config.IMGWIDTH)
            summary = story.find('p')
            if summary:
                story_dict['summary'] = summary.text
            # Add the dict to our list
            stories_list.append(story_dict)
        else:
            logging.info("No match found")
    return stories_list


def update_stories_in_db(stories_list):
    logging.info('Updating stories in db, if required ...')

    for story in stories_list:
        logging.debug("working on story: ")
        logging.debug(story)
        logging.debug("checking if already reported")

        # check for url to remove reposts
        url = story['url']
        already_there_url = collection.count_documents({"url": url})
        if already_there_url == 0:
            logging.info("Adding story to db collection")
            story['timestamp'] = time.time()
            insert_result = collection.insert_one(story)
            if insert_result.acknowledged:
                if Config.DISCORD_NOTIFY == 'True':
                    do_discord_notification(story)
                if Config.TWITTER_NOTIFY == 'True':
                    do_twitter_notification(story)
        else:
            logging.info("Story already in DB ... " + url )


def do_twitter_notification(story):
    logging.info("Doing a Twitter notification...")
    embed_url = "https://www.bbc.co.uk" + story['url']
    response = client.create_tweet(
            text=Config.TWITTER_STATUS_PREFIX + " " + story['headline']+ "  " + embed_url
            )
    print(f"https://twitter.com/user/status/{response.data['id']}")
    print(f"https://twitter.com/user/status/{response.data['id']}")
    logging.info("Twitter notification complete.")
    logging.info("Tweeted: " + story['headline'])


def do_discord_notification(story):
    logging.info("Doing a discord notification...")
    logging.info(story)

    embed_headline = story['headline']
    embed_url = "https://www.bbc.co.uk" + story['url']

    # check optional bits
    if 'summary' in story:
        embed_summary = story['summary']
    else:
        embed_summary = " "

    if 'img' in story:
        embed_image = story['img']
    else:
        embed_image = " "

    url = Config.DISCORD_WEBHOOK_URL

    data = {"content": Config.DISCORD_CONTENT, "username": Config.DISCORD_USERNAME, "embeds": []}

    embed = {"description": embed_summary,
             "title": embed_headline,
             "url": embed_url,
             "image": {'url': embed_image},
             "footer": {'text': embed_url}}
    data["embeds"].append(embed)

    result = requests.post(url, data=json.dumps(data), headers={"Content-Type": "application/json"})

    try:
        result.raise_for_status()
    except requests.exceptions.HTTPError as err:
        logging.info(err)
    else:
        logging.info("Notification delivered successfully, code {}.".format(result.status_code))

    logging.info("Done the discord notification:")


def main():
    while True:
        # the main bit
        get_stories_list = scrape_bbc_news()

        # chuck results in db
        if get_stories_list:
            update_stories_in_db(get_stories_list)
        else:
            logging.info("No stories found.")

        # loop delay
        logging.info("Waiting for next run.")
        time.sleep(int(Config.REPEAT_DELAY))

if __name__ == '__main__':
    main()
