ARG DOCKER_CE_RPM_IMAGE=shared/build/rpm/docker-ce

FROM ${DOCKER_CE_RPM_IMAGE} as docker_ce_rpm_image
FROM centos:7.6.1810

ADD kubernetes.repo /etc/yum.repos.d/kubernetes.repo

RUN yum clean all && \
    yum update -y && \
    yum install -y kubectl && \
    yum install -y epel-release && \
    yum install -y syum-utils device-mapper-persistent-data lvm2 

COPY --from=docker_ce_rpm_image /out/* .
RUN yum install -y ./docker-ce-*

ADD push.sh /push.sh

RUN chmod +x /push.sh
