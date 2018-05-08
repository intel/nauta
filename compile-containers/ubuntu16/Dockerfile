ARG BASE_IMAGE
FROM ${BASE_IMAGE}

RUN apt-get update
RUN apt-get install -y build-essential

RUN apt-get install -y software-properties-common python-software-properties

RUN add-apt-repository -y ppa:deadsnakes/ppa
RUN apt-get update
RUN apt-get install -y python3.6 python3.6-dev curl
RUN curl https://bootstrap.pypa.io/get-pip.py | python3.6
RUN pip3.6 install -U pip==9.0.1
RUN pip3.6 install -U setuptools virtualenv wheel
RUN pip3.6 install -U ansible==2.5.0.0 docker==3.3.0 jmespath==0.9.3
