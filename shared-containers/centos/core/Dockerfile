FROM centos:7.6.1810

RUN yum update -y && yum install -y centos-release-scl
RUN yum-config-manager --enable centos-sclo-rh-testing
RUN yum install -y epel-release

CMD ["/bin/bash"]
