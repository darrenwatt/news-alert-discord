FROM python:3.6-alpine

COPY requirements.txt /
COPY news-alert-discord.py /

RUN pip install -r requirements.txt

CMD [ "python", "./news-alert-discord.py" ]
