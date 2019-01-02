FROM centos:7.5.1804

RUN yum install -y centos-release-scl
RUN yum-config-manager --enable centos-sclo-rh-testing
RUN yum install -y epel-release

CMD ["/bin/bash"]
