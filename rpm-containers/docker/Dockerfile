ARG DOCKER_CE_RPM_IMAGE=shared/build/rpm/docker-ce
ARG DOCKER_CE_DEBUG_INFO_RPM_IMAGE=shared/build/rpm/docker-ce-debuginfo
ARG CONTAINER_SELINUX_RPM_IMAGE=shared/build/rpm/container-selinux

FROM ${DOCKER_CE_RPM_IMAGE} as docker_ce_rpm_image
FROM ${DOCKER_CE_DEBUG_INFO_RPM_IMAGE} as docker_ce_debuginfo_rpm_image
FROM ${CONTAINER_SELINUX_RPM_IMAGE} as container_selinux_rpm_image
FROM centos:7.5.1804

WORKDIR /out

COPY --from=docker_ce_rpm_image /out/* .
COPY --from=docker_ce_debuginfo_rpm_image /out/* .
COPY --from=container_selinux_rpm_image /out/* .
