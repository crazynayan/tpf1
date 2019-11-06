FROM python:3.8

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY asm asm
COPY macro macro
COPY utils utils
COPY assembly assembly
COPY execution execution
COPY db db
COPY test test
COPY config.py google-cloud.json ./


ENV GOOGLE_APPLICATION_CREDENTIALS google-cloud.json

RUN exec python -m unittest discover -s test -v -f
