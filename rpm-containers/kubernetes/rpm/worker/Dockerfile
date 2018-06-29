ARG BASE_IMAGE
FROM ${BASE_IMAGE}

ADD ./*.spec ./SPECS/

RUN build-rpm.sh kubernetes-kubelet ${OUTPUT}/ && \
    build-rpm.sh kubernetes-worker ${OUTPUT}/
