FROM python:3.10

WORKDIR /tpf1

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir gunicorn

COPY d20_source d20_source
COPY d21_backend d21_backend
COPY google-cloud-tokyo.json ./

# Dev database
# ENV GOOGLE_APPLICATION_CREDENTIALS google-cloud.json
# Prod database
ENV GOOGLE_APPLICATION_CREDENTIALS google-cloud-tokyo.json

ENV DOMAIN tiger
RUN exec python -m unittest discover -s d21_backend.p8_test.test_local -v -f

ENV DOMAIN general
RUN exec python -m unittest d21_backend.p8_test.test_general.test_tsj1 -v -f

ENV CI_CLOUD_STORAGE use
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --access-logfile - --error-logfile - d21_backend.p7_flask_app:tpf1_app
