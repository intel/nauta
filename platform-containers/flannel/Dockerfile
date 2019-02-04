ARG DATA_IMAGE
ARG BASE_IMAGE
FROM ${DATA_IMAGE} as dataimage
FROM ${BASE_IMAGE}

RUN yum clean all && yum update -y && yum install -y which iproute2 net-tools iptables

COPY --from=dataimage /build-output/flannel/flannel /opt/bin/
COPY --from=dataimage /build-output/flannel/flanneld /opt/bin/

RUN chmod +x /opt/bin/*

