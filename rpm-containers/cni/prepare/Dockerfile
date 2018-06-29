ARG CNI_DATA_IMAGE
ARG BASE_IMAGE
FROM ${CNI_DATA_IMAGE} as data

FROM ${BASE_IMAGE}

COPY --from=data /build-output/cni-plugins.tar.gz ./SOURCES/cni-plugins.tar.gz

ENV RPM_VERSION=0.7.1
ENV RPM_RELEASE=0
