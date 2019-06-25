ARG BASE_IMAGE
FROM ${BASE_IMAGE}

COPY ./*.spec ./SPECS/

RUN build-rpm.sh kubernetes-kubectl ${OUTPUT}/ && \
    build-rpm.sh kubernetes-client ${OUTPUT}/
