ARG DATA_IMAGE
ARG BASE_IMAGE
FROM ${DATA_IMAGE} as dataimage
FROM ${BASE_IMAGE}

RUN yum update -y && \
    yum install -y iptables dnsmasq dnsmasq-utils && \
    yum clean all

COPY --from=dataimage /build-output/addons/dnsmasq-nanny /
RUN chmod +x /dnsmasq-nanny

RUN mkdir -vp /etc/k8s/dns/dnsmasq-nanny
ADD dnsmasq.conf /etc/k8s/dns/dnsmasq-nanny/

RUN echo "user=root" > /etc/dnsmasq.conf

ENTRYPOINT /dnsmasq-nanny
