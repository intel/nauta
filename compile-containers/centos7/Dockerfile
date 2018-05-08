ARG BASE_IMAGE
FROM ${BASE_IMAGE}

RUN yum clean all
RUN yum update -y
RUN yum install -y epel-release
RUN yum install -y @development https://centos7.iuscommunity.org/ius-release.rpm
RUN yum install -y python36u python36u-pip python36u-devel
RUN pip3.6 install -U pip==9.0.1
RUN pip3.6 install -U setuptools virtualenv wheel
RUN pip3.6 install -U ansible==2.5.0.0 docker==3.3.0 jmespath==0.9.3
