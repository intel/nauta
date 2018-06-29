ARG BASE_IMAGE
FROM ${BASE_IMAGE}

ADD ./*.spec ./SPECS/

RUN build-rpm.sh kubernetes-kubectl ${OUTPUT}/ && \
    build-rpm.sh kubernetes-client ${OUTPUT}/
