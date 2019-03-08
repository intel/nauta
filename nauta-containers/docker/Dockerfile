ARG BASE_IMAGE=centos:7.6.1810
FROM ${BASE_IMAGE}

RUN yum clean all && \
    yum update -y && \
    yum install -y syum-utils device-mapper-persistent-data lvm2
RUN yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
RUN yum install -y docker-ce-18.03.0.ce-1.el7.centos

ADD push.sh /push.sh

RUN chmod +x /push.sh
