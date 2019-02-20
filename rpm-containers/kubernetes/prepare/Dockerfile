ARG BASE_IMAGE
FROM ${BASE_IMAGE}

RUN curl -L https://github.com/kubernetes/kubernetes/releases/download/v1.10.13/kubernetes.tar.gz -o kubernetes.tar.gz
RUN tar -xvf kubernetes.tar.gz && rm kubernetes.tar.gz

RUN yes | ./kubernetes/cluster/get-kube-binaries.sh

ENV RPM_VERSION=1.10.13
ENV RPM_RELEASE=0
