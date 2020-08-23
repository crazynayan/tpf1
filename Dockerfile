FROM python:3.8

WORKDIR /tpf1

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir gunicorn

COPY p0_source p0_source
COPY utils utils
COPY assembly assembly
COPY execution execution
COPY db db
COPY flask_app flask_app
COPY p8_test p8_test
COPY config.py google-cloud-tokyo.json google-cloud.json ./

# Dev database
ENV GOOGLE_APPLICATION_CREDENTIALS google-cloud.json
# Prod database
#ENV GOOGLE_APPLICATION_CREDENTIALS google-cloud-tokyo.json

RUN exec python -m unittest discover -s p8_test -v -f

CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --access-logfile - --error-logfile - flask_app:tpf1_app
