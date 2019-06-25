ARG BASE_IMAGE
FROM ${BASE_IMAGE}

COPY elasticsearch_proxy.py /elasticsearch_proxy.py
COPY requirements.txt /requirements.txt
RUN pip install --no-binary=:all: --no-cache-dir -r /requirements.txt

WORKDIR /

CMD gunicorn -b 0.0.0.0:9201 elasticsearch_proxy:app
