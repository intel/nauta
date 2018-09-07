ARG BASE_IMAGE
ARG NGINX_BUILD_IMAGE
FROM ${NGINX_BUILD_IMAGE} as data
FROM ${BASE_IMAGE}

RUN mkdir -vp /out/
COPY --from=data /build-output/nginx-1.13.9-1.ngx.x86_64.rpm /out/nginx-1.13.9-1.el7_4.ngx.x86_64.rpm
