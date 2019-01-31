ARG BASE_IMAGE
FROM ${BASE_IMAGE}

ENV RPM_VERSION=2.7
ENV RPM_RELEASE=0

RUN yum clean all
RUN yum update -y && yum install -y python-devel python libffi-devel openssl-devel gcc gcc-c++
RUN curl "https://bootstrap.pypa.io/get-pip.py" | python
RUN pip install -U pip==10.0.1 virtualenv==16.0.0 setuptools==39.2.0 wheel==0.31.1

ADD ./*.spec ./SPECS/

RUN build-rpm.sh pip-repository ${OUTPUT}/

ADD *.rpm ${OUTPUT}/
