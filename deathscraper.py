import requests
import time
import pymongo
from bs4 import BeautifulSoup
from discord import Webhook, RequestsWebhookAdapter
from dotenv import load_dotenv
from discord_webhook import DiscordWebhook, DiscordEmbed
import json
import re
import os

msg = "Yoyoyo, starting up in the house!"
print(msg)

# import secret stuff
load_dotenv()

searchterms = ["dead", "dies"]
reg = re.compile(r'(?i)\b(?:%s)\b' % '|'.join(searchterms))

# database stuff
db_name = os.getenv("db_name")
db_host = os.getenv("db_host")
db_port = int(os.getenv("db_port"))
db_user = os.getenv("db_user")
db_pass = os.getenv("db_pass")

webhook_url = os.getenv("webhook_url")

notify = os.getenv("notify")

client = pymongo.MongoClient(db_host, db_port, retryWrites=False)
database = client[db_name]
database.authenticate(db_user, db_pass)

stories_collection = database['stories']
# from bbc site, datawidths = "[240,380,420,490,573,743,820]", pick one
imgwidth = "420"


def scrape_bbc_news():
    print("Getting stories featuring the words:")
    print(*searchterms)
    try:
        response = requests.get('https://www.bbc.co.uk/news')
    except requests.exceptions.RequestException as e:
        print(e)
        print("Never mind... we'll try again in a bit.")
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
        # if any(term in headline.text.lower() for term in searchterms):
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
        headline = story['headline']
        already_there_headlines = stories_collection.count_documents({"headline": headline})
        # check for url to remove reposts
        url = story['url']
        already_there_url = stories_collection.count_documents({"url": url})
        # print(already_there_check)
        already_there_check = already_there_headlines + already_there_url
        if already_there_check == 0:
            print("Adding story to database collection")
            story['timestamp'] = time.time()
            insert_result = stories_collection.insert_one(story)
            if insert_result.acknowledged:
                if notify:
                    do_discord_notification_2(story)
        else:
            print("No new stories to add.")


def do_discord_notification(story):
    print("Doing a discord notification...")
    print(story)

    embed_headline = story['headline']
    embed_url = story['url']

    if 'summary' in story:
        embed_summary = story['summary']
    else:
        embed_summary = " "

    if 'img' in story:
        embed_image = story['img']
    else:
        embed_image = " "

    webhook = DiscordWebhook(url=webhook_url)

    embed = DiscordEmbed(title=embed_headline, description=embed_summary, color=242424)

    embed.set_image(url=embed_image)

    embed.set_footer(text="https://www.bbc.co.uk/news"+embed_url, url="https://www.bbc.co.uk/news"+embed_url)

    webhook.add_embed(embed)

    webhook.execute()

#    webhook.send(embed_notif, username='test')
    print("Done a discord notification.")


def do_discord_notification_2(story):
    print("Doing a discord notification...")
    print(story)

    embed_headline = story['headline']
    embed_url = story['url']

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
    data = {}
    data["content"] = "They be dead!"
    data["username"] = "Death Bot 3000"

    # for all params, see https://discordapp.com/developers/docs/resources/channel#embed-object
    embed = []
    embed["description"] = "text in embed"
    embed["title"] = "embed title"
    # embed["url"] = "https://www.bbc.co.uk/news"+embed_url
    # embed["image"] = embed_image
    # embed["footer"] = "https://www.bbc.co.uk/news"+embed_url
    data["embeds"].append(embed)

    result = requests.post(url, data=json.dumps(data), headers={"Content-Type": "application/json"})

    try:
        result.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)
    else:
        print("Notification delivered successfully, code {}.".format(result.status_code))

    print("Done a discord notification.")


'''
    webhook = DiscordWebhook(url=webhook_url)
    embed = DiscordEmbed(title=embed_headline, description=embed_summary, color=242424)
    embed.set_image(url=embed_image)
    embed.set_footer(text="https://www.bbc.co.uk/news"+embed_url, url="https://www.bbc.co.uk/news"+embed_url)
    webhook.add_embed(embed)
    webhook.execute()
'''


def main():
    while True:
        # the main bit
        get_stories_list = scrape_bbc_news()

        # chuck results in db
        if get_stories_list:
            update_stories_in_db(get_stories_list)

        # loop delay, 5 mins
        print("Waiting for next run.")
        time.sleep(300)


main()
