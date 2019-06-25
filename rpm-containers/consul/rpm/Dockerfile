ARG BASE_IMAGE
FROM ${BASE_IMAGE}

COPY consul.spec ./SPECS/

RUN build-rpm.sh consul ${OUTPUT}/
