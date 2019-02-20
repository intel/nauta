ARG NGINX_RPM_IMAGE=shared/build/rpm/nginx

FROM ${NGINX_RPM_IMAGE} as nginx_rpm_image
FROM centos:7.6.1810

WORKDIR /out

COPY --from=nginx_rpm_image /out/* .
