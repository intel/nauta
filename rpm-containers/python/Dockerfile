ARG BASE_IMAGE
FROM ${BASE_IMAGE}

ENV RPM_VERSION=2.7
ENV RPM_RELEASE=0

RUN yum update -y && \
    yum install -y python-pip python-devel python libffi-devel openssl-devel gcc gcc-c++ && \
    yum clean all

RUN pip install --no-binary :all: -U pip==19.0.3 virtualenv==16.0.0 setuptools==39.2.0 wheel==0.31.1

COPY ./*.spec ./SPECS/

RUN build-rpm.sh pip-repository ${OUTPUT}/

COPY *.rpm ${OUTPUT}/
