ARG DATA_IMAGE
ARG BASE_IMAGE
FROM ${DATA_IMAGE} as dataimage
FROM ${BASE_IMAGE}


RUN yum update -y && \
    yum install -y iptables && \
    yum clean all

COPY --from=dataimage /build-output/kubernetes/kube-proxy /
RUN chmod +x /kube-proxy
RUN cp /kube-proxy /bin && chmod +x /bin/kube-proxy
RUN cp /kube-proxy /usr/bin/ && chmod +x /bin/kube-proxy


ENTRYPOINT /kube-proxy
