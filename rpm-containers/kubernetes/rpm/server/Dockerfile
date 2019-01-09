ARG BASE_IMAGE
FROM ${BASE_IMAGE}

ADD ./*.spec ./SPECS/

RUN mv /root/rpmbuild/kubernetes/server/kubernetes-server-linux-amd64.tar.gz ./SOURCES/kubernetes-server-linux-amd64.tar.gz

RUN build-rpm.sh kubernetes-apiserver ${OUTPUT}/ && \
    build-rpm.sh kubernetes-controller-manager ${OUTPUT}/ && \
    build-rpm.sh kubernetes-scheduler ${OUTPUT}/ && \
    build-rpm.sh kubernetes-server ${OUTPUT}/
