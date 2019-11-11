FROM python:3.8

WORKDIR /tpf1

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir gunicorn

COPY asm asm
COPY macro macro
COPY utils utils
COPY assembly assembly
COPY execution execution
COPY db db
COPY firestore firestore
COPY flask_app flask_app
COPY test test
COPY config.py google-cloud.json ./

ENV GOOGLE_APPLICATION_CREDENTIALS google-cloud.json

EXPOSE 5000

RUN exec python -m unittest discover -s test -v -f

ENTRYPOINT exec gunicorn -b :5000 --access-logfile - --error-logfile - flask_app:tpf1_app
