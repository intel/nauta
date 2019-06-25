ARG BASE_IMAGE
FROM ${BASE_IMAGE}

COPY cni-plugins.spec ./SPECS/

RUN build-rpm.sh cni-plugins ${OUTPUT}/
