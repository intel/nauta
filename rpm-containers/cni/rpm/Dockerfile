ARG BASE_IMAGE=shared/centos/rpm-packer

FROM ${BASE_IMAGE}

RUN curl -L https://github.com/containernetworking/plugins/releases/download/v0.7.1/cni-plugins-amd64-v0.7.1.tgz -o ./cni-plugins.tar.gz

RUN mv ./cni-plugins.tar.gz ./SOURCES/cni-plugins.tar.gz

ENV RPM_VERSION=0.7.1
ENV RPM_RELEASE=0

ADD cni-plugins.spec ./SPECS/

RUN build-rpm.sh cni-plugins ${OUTPUT}/