ARG BASE_IMAGE
FROM ${BASE_IMAGE}

RUN yum clean all && \
    yum update -y && \
    yum install -y python-devel python-pip libffi-devel openssl-devel gcc gcc-++ bison flex
RUN pip install -U pip==10.0.1
