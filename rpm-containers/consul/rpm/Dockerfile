ARG BASE_IMAGE
FROM ${BASE_IMAGE}

ADD consul.spec ./SPECS/

RUN build-rpm.sh consul ${OUTPUT}/
