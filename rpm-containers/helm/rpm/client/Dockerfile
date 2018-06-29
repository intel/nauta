ARG BASE_IMAGE
FROM ${BASE_IMAGE}

ADD ./*.spec ./SPECS/

RUN build-rpm.sh helm ${OUTPUT}/
