FROM python:3.6-alpine

RUN pip install requests
RUN pip install pymongo
RUN pip install bs4
RUN pip install python-dotenv

ADD news-alert-discord.py /

CMD [ "python", "./news-alert-discord.py" ]
