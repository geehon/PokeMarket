FROM python:3.11-slim

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
RUN pip install gunicorn psycopg2-binary

COPY app app
COPY migrations migrations
COPY pokemarket.py config.py boot.sh ./
RUN chmod a+x ./boot.sh

ENV FLASK_APP pokemarket.py

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]
