ARG BASE_IMAGE=centos:7.6.1810
ARG DOCKER_RPM_IMAGE
FROM ${DOCKER_RPM_IMAGE} as dockerrpm
FROM ${BASE_IMAGE}

RUN yum clean all && \
    yum update -y && \
    yum install -y syum-utils device-mapper-persistent-data lvm2

COPY --from=dockerrpm /root/rpmbuild/RPMS/x86_64/docker-ce-18.06.3-nauta.el7.x86_64.rpm /
RUN yum install -y /docker-ce-18.06.3-nauta.el7.x86_64.rpm

ADD push.sh /push.sh

RUN chmod +x /push.sh
 
