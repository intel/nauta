ARG BASE_IMAGE
ARG DATA_IMAGE
FROM ${DATA_IMAGE} as dataimage
FROM ${BASE_IMAGE}

COPY --from=dataimage /build-output/rpm/docker-ce-18.06.3-nauta.el7.x86_64.rpm /out/
COPY --from=dataimage /build-output/rpm/docker-ce-debuginfo-18.06.3-nauta.el7.x86_64.rpm /out/
COPY --from=dataimage /build-output/rpm/container-selinux-2.66-1.el7.noarch.rpm /out/
