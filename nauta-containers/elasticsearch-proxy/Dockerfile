ARG BASE_IMAGE
FROM ${BASE_IMAGE}

ADD elasticsearch_proxy.py /elasticsearch_proxy.py
ADD requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

WORKDIR /

CMD gunicorn -b 0.0.0.0:9201 elasticsearch_proxy:app
