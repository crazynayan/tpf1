FROM python:3.8

WORKDIR /tpf1

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir gunicorn

COPY p0_source p0_source
COPY p1_utils p1_utils
COPY p2_assembly p2_assembly
COPY p3_db p3_db
COPY p4_execution p4_execution
COPY p7_flask_app p7_flask_app
COPY p8_test p8_test
COPY config.py google-cloud-tokyo.json tpf.py ./

# Dev database
# ENV GOOGLE_APPLICATION_CREDENTIALS google-cloud.json
# Prod database
ENV GOOGLE_APPLICATION_CREDENTIALS google-cloud-tokyo.json
ENV DOMAIN sabre

RUN exec python -m unittest discover -s p8_test.test_local -v -f

ENV CI_CLOUD_STORAGE use
ENV DOMAIN general

CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --access-logfile - --error-logfile - p7_flask_app:tpf1_app
