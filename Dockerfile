FROM python:3

RUN pip install requests
RUN pip install pymongo
RUN pip install bs4
RUN pip install python-dotenv


ADD deathscraper.py /

CMD [ "python", "./deathscraper.py" ]
