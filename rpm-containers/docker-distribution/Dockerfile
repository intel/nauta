ARG DOCKER_DISTRIBUTION_RPM_IMAGE=shared/build/rpm/docker-distribution

FROM ${DOCKER_DISTRIBUTION_RPM_IMAGE} as docker_distribution_rpm_image
FROM centos:7.6.1810

WORKDIR /out

COPY --from=docker_distribution_rpm_image /out/* .
