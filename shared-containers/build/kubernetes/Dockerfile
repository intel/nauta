ARG BASE_IMAGE
FROM ${BASE_IMAGE}

RUN mkdir -p ${GOPATH}/src/k8s.io/kubernetes \
             /build-output/kubernetes

ADD kubernetes.tar.gz ${GOPATH}/src/k8s.io/

RUN yum update -y && \
    yum install -y which && \
    yum clean all

RUN mv /build/work/src/k8s.io/kubernetes-1.13.10/* /build/work/src/k8s.io/kubernetes/

WORKDIR ${GOPATH}/src/k8s.io/kubernetes

RUN make && \
    cp ${GOPATH}/src/k8s.io/kubernetes/_output/local/go/bin/* /build-output/kubernetes/ && \
    cd /build-output && \
    tar -I pigz -cf kubernetes.tar.gz kubernetes/ && \
    rm -rf ${GOPATH}/src/k8s.io/kubernetes
