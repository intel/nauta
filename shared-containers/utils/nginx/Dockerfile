ARG BASE_IMAGE
ARG NGINX_BUILD_IMAGE
FROM ${NGINX_BUILD_IMAGE} as data
FROM ${BASE_IMAGE}

COPY --from=data /build-output/nginx-1.13.9-1.ngx.x86_64.rpm /tmp/nginx-1.13.9-1.el7_4.ngx.x86_64.rpm

RUN yum install -y /tmp/nginx-1.13.9-1.el7_4.ngx.x86_64.rpm && rm -rf /tmp/nginx-1.13.9-1.el7_4.ngx.x86_64.rpm

EXPOSE 80

STOPSIGNAL SIGTERM

CMD ["nginx", "-g", "daemon off;"]
