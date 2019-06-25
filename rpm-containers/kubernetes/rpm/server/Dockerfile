ARG BASE_IMAGE
FROM ${BASE_IMAGE}

COPY ./*.spec ./SPECS/

RUN build-rpm.sh kubernetes-apiserver ${OUTPUT}/ && \
    build-rpm.sh kubernetes-controller-manager ${OUTPUT}/ && \
    build-rpm.sh kubernetes-scheduler ${OUTPUT}/ && \
    build-rpm.sh kubernetes-server ${OUTPUT}/
