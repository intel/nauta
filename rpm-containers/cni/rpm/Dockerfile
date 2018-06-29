ARG BASE_IMAGE
FROM ${BASE_IMAGE}

ADD cni-plugins.spec ./SPECS/

RUN build-rpm.sh cni-plugins ${OUTPUT}/
