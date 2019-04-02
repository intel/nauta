ARG BASE_IMAGE
FROM ${BASE_IMAGE}

RUN yum clean all && \
    yum update -y && \
    yum install -y python-devel python-pip libffi-devel openssl-devel gcc gcc-c++ bison flex

RUN pip install --no-binary :all: -U pip==19.0.3
