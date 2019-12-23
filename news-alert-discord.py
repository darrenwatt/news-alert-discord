import requests
import time
import pymongo
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import json
import re
import os
from configparser import ConfigParser
import tweepy

msg = "Yoyoyo, starting up in the house!"
print(msg)

config = ConfigParser()
print(config.read('config.ini'))

print("Loading configuration")
notify = config.getboolean('general', 'notify', fallback=False)
notify_twitter = config.getboolean('general', 'twitter_notify', fallback=False)
loop_timer = config.getint('general', 'loop_timer', fallback=300)
news_url = config.get('general', 'news_url', fallback='https://www.bbc.co.uk/news')
imgwidth = config.get('general', 'imgwidth', fallback="420")
searchterms = json.loads(config.get('general', 'searchterms', fallback="boris"))
searchspecific = config.getboolean('general', 'searchspecific', fallback=True)
content = config.get('general', 'content', fallback="This is an update ...")
username = config.get('general', 'username', fallback="News Update Bot")
database_name = config.get('general', 'database_name', fallback="stories")

# import secret stuff, mongo config and discord webhook
load_dotenv()

if searchspecific:
    # match exact terms only
    reg = re.compile(r'(?i)\b(?:%s)\b' % '|'.join(searchterms))
else:
    # match any partial term, this seems to work, I suck at regex so this might well be wrong
    reg = re.compile(r'(?i)%s' % '|'.join(searchterms))

print("regex output:")
print(reg)


# database stuff
db_name = os.getenv("db_name")
db_host = os.getenv("db_host")
db_port = int(os.getenv("db_port"))
db_user = os.getenv("db_user")
db_pass = os.getenv("db_pass")

webhook_url = os.getenv("webhook_url")


# twitter import

consumer_key = os.getenv("twitter_key")
consumer_secret = os.getenv("twitter_secret")
access_token = os.getenv("twitter_token")
access_token_secret = os.getenv("twitter_token_secret")

# twitter auth

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)
try:
    api.verify_credentials()
    print("Authentication OK")
except:
    print("Error during authentication")


if notify_twitter:
    print("Tweeting is enabled")
else:
    print("Tweeting is disabled")

print("notify is set to {}".format(notify))
print("loop_timer is set to {}".format(loop_timer))
print("news_url is set to {}".format(news_url))
print("imgwidth is set to {}".format(imgwidth))
print("content is set to {}".format(content))
print("username is set to {}".format(username))
print("database_name is set to {}".format(database_name))
print("searchspecific is set to {}".format(searchspecific))

print("searchterms are:")
print(*searchterms)

client = pymongo.MongoClient(db_host, db_port, retryWrites=False)
database = client[db_name]
database.authenticate(db_user, db_pass)

stories_collection = database[database_name]


def scrape_bbc_news():
    print("Getting stories now.")
    try:
        response = requests.get(news_url)
    except requests.exceptions.RequestException as e:
        print(e)
        print("Failed. Never mind... we'll try again in a bit.")
        return
    doc = BeautifulSoup(response.text, 'html.parser')

    # Start with an empty list
    stories_list = []
    stories = doc.find_all('div', {'class': 'gs-c-promo'})
    for story in stories:
        # Create a dictionary without anything in it
        story_dict = {}
        headline = story.find('h3')
        # print(headline.text.lower())
        for keyword in headline:
            if reg.search(keyword):
                print("match found")
                story_dict['headline'] = headline.text
                print(headline.text)
                link = story.find('a')
                if link:
                    story_dict['url'] = link['href']
                img = story.find('img')
                if img:
                    print(img)
                    try:
                        print(img['data-src'])
                    except NameError:
                        print("Variable data-src is not defined")
                    except KeyError:
                        print("probably want data instead")
                        story_dict['img'] = img['src']
                    else:
                        story_dict['img'] = img['data-src'].replace("{width}", imgwidth)
                summary = story.find('p')
                if summary:
                    story_dict['summary'] = summary.text
                # Add the dict to our list
                stories_list.append(story_dict)
    return stories_list


def update_stories_in_db(stories_list):
    print('Updating stories in db, if required ...')

    for story in stories_list:
        # print("working on story: ")
        # print(story)
        # print("checking if already reported")

        # check for url to remove reposts
        url = story['url']
        already_there_url = stories_collection.count_documents({"url": url})
        if already_there_url == 0:
            print("Adding story to database collection")
            story['timestamp'] = time.time()
            insert_result = stories_collection.insert_one(story)
            if insert_result.acknowledged:
                if notify:
                    do_discord_notification(story)
                if notify_twitter:
                    do_twitter_notification(story)
        else:
            print("Story already in DB.")


def do_twitter_notification(story):
    print("Doing a Twitter notification...")
    embed_url = "https://www.bbc.co.uk" + story['url']
    api.update_status(status = story['headline']+ " " + embed_url)


def do_discord_notification(story):
    print("Doing a discord notification...")
    print(story)

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

    url = webhook_url

    data = {"content": content, "username": username, "embeds": []}

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
        print(err)
    else:
        print("Notification delivered successfully, code {}.".format(result.status_code))

    print("Done the discord notification:")


def main():
    while True:
        # the main bit
        get_stories_list = scrape_bbc_news()

        # chuck results in db
        if get_stories_list:
            update_stories_in_db(get_stories_list)
        else:
            print("No stories found.")

        # loop delay
        print("Waiting for next run.")
        time.sleep(loop_timer)


main()
