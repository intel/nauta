ARG BASE_IMAGE
FROM ${BASE_IMAGE}

ADD ./*.spec ./SPECS/

RUN mv /root/rpmbuild/kubernetes/server/kubernetes-server-linux-amd64.tar.gz ./SOURCES/kubernetes-server-linux-amd64.tar.gz

RUN build-rpm.sh kubernetes-kubelet ${OUTPUT}/ && \
    build-rpm.sh kubernetes-worker ${OUTPUT}/
