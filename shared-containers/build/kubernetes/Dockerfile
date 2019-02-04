ARG BASE_IMAGE
FROM ${BASE_IMAGE}

COPY kubernetes.tar.gz ./

RUN yum clean all && \
    yum update -y && \
    yum install -y which

RUN mkdir ${GOPATH}/src/k8s.io/kubernetes -p && \
    tar -zxf kubernetes.tar.gz -C ${GOPATH}/src/k8s.io/kubernetes --strip-components=1 && \
    (cd ${GOPATH}/src/k8s.io/kubernetes && make)

RUN mkdir -p /build-output/kubernetes && \
    cp ${GOPATH}/src/k8s.io/kubernetes/_output/local/go/bin/* /build-output/kubernetes/ && \
    cd /build-output && \
    tar -I pigz -cf kubernetes.tar.gz kubernetes/
