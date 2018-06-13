ARG BASE_IMAGE=centos:7.4.1708
FROM ${BASE_IMAGE}

RUN yum clean all
RUN yum update -y
RUN yum install -y epel-release
RUN yum install -y https://centos7.iuscommunity.org/ius-release.rpm
RUN yum install -y python36u python36u-pip python36u-devel
RUN pip3.6 install -U pip==10.0.1
