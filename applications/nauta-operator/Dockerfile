FROM python:3.7
ADD . /src
ADD requirements.txt /src/requirements.txt
RUN pip install -r /src/requirements.txt
CMD kopf run /src/nauta_operator.py