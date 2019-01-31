ARG BASE_IMAGE
FROM ${BASE_IMAGE}

RUN mkdir /build-output/consul

COPY consul-1.1.0_linux_amd64.zip /build-output/consul/consul-1.1.0_linux_amd64.zip

RUN cd /build-output/consul && unzip consul-1.1.0_linux_amd64.zip

RUN rm -rf /build-output/consul/consul-1.1.0_linux_amd64.zip

RUN yum clean all && yum update -y && yum install -y which

RUN cd /build-output && \
    tar -I pigz -cf consul.tar.gz consul/
