ARG BASE_IMAGE=shared/centos/rpm-packer
FROM ${BASE_IMAGE}

ENV RPM_VERSION=2.11.0
ENV RPM_RELEASE=0

RUN mkdir -p SOURCES && mkdir -p out && mkdir -p helm

RUN wget --quiet https://storage.googleapis.com/kubernetes-helm/helm-v2.11.0-linux-amd64.tar.gz -O ./helm-amd64.tar.gz
# unpack helm tarball, change directory structure and create tarball again
RUN tar -xvf ./helm-amd64.tar.gz
RUN cp -vR ./linux-amd64/* ./helm
RUN tar -cf ./SOURCES/helm.tar.gz ./helm/*

ADD ./*.spec ./SPECS/

RUN build-rpm.sh helm ${OUTPUT}/
