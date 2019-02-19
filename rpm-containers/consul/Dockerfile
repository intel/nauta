ARG CONSUL_SOURCES_IMAGE=shared/build/consul
ARG BASE_IMAGE=shared/centos/rpm-packer

FROM ${CONSUL_SOURCES_IMAGE} as consul_sources_data
FROM ${BASE_IMAGE}

COPY --from=consul_sources_data /build-output/consul.tar.gz ./SOURCES/consul.tar.gz
ADD consul.spec ./SPECS/

ENV RPM_VERSION=1.1.0
ENV RPM_RELEASE=0

RUN build-rpm.sh consul ${OUTPUT}/
