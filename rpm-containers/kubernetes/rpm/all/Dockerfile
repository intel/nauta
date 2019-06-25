ARG BASE_IMAGE
FROM ${BASE_IMAGE}

COPY ./*.spec ./SPECS/

RUN build-rpm.sh kubernetes ${OUTPUT}/
