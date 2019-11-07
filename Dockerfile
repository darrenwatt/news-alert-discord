FROM python:3.6-alpine

RUN pip install requests
RUN pip install pymongo
RUN pip install bs4
RUN pip install python-dotenv

ADD news-ping-discord.py /

CMD [ "python", "./news-ping-discord.py" ]
