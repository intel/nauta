ARG BASE_IMAGE
FROM ${BASE_IMAGE}

RUN mkdir /build-output/consul

COPY consul /build-output/consul/consul

RUN yum clean all && yum install -y which

RUN cd /build-output && \
    tar -I pigz -cf consul.tar.gz consul/
