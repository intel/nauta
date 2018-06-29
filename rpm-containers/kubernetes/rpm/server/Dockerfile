ARG BASE_IMAGE
FROM ${BASE_IMAGE}

ADD ./*.spec ./SPECS/

RUN build-rpm.sh kubernetes-apiserver ${OUTPUT}/ && \
    build-rpm.sh kubernetes-controller-manager ${OUTPUT}/ && \
    build-rpm.sh kubernetes-scheduler ${OUTPUT}/ && \
    build-rpm.sh kubernetes-server ${OUTPUT}/
