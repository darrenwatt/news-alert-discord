import requests
from dotenv import load_dotenv
import json
import os

msg = "Sending test msg to discord"
print(msg)

# import secret stuff
load_dotenv()

# database stuff
db_name = os.getenv("db_name")
db_host = os.getenv("db_host")
db_port = int(os.getenv("db_port"))
db_user = os.getenv("db_user")
db_pass = os.getenv("db_pass")

webhook_url = os.getenv("webhook_url")

notify = os.getenv("notify", True)
print("notify is set to {}".format(notify))


def do_discord_notification():
    print("Doing a discord notification...")

    embed_headline = "Man eats beans"
    embed_url = "https://www.bbc.co.uk/news/man-eats-beans"
    embed_summary = "I was going to eat a biscuit, but then I ate some beans - said the man"
    embed_image = "https://newengland.com/wp-content/uploads/old-fashioned-baked-beans-recipe-1.jpg"

    url = webhook_url
    data = {"content": "Man eats beans", "username": "Test", "embeds": []}

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

    print("Done a discord notification:")


def main():
    # the main bit
    do_discord_notification()


main()
