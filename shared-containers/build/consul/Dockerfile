FROM centos:7.6.1810

RUN yum clean all && yum update -y && yum install -y which wget unzip pigz

RUN mkdir -p /build-output/consul

RUN wget --quiet https://releases.hashicorp.com/consul/1.1.0/consul_1.1.0_linux_amd64.zip -O /build-output/consul/consul-1.1.0_linux_amd64.zip

RUN cd /build-output/consul && unzip consul-1.1.0_linux_amd64.zip

RUN rm -rf /build-output/consul/consul-1.1.0_linux_amd64.zip

RUN cd /build-output && \
    tar -I pigz -cf consul.tar.gz consul/
