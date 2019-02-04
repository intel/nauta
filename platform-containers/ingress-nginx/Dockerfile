ARG INGRESS_DATA_IMAGE
ARG DUMBINIT_DATA_IMAGE
ARG NGINX_DATA_IMAGE
ARG BASE_IMAGE
FROM ${INGRESS_DATA_IMAGE} as ingressdataimage
FROM ${DUMBINIT_DATA_IMAGE} as dumbinitdataimage
FROM ${NGINX_DATA_IMAGE} as nginxdataimage
FROM ${BASE_IMAGE}

COPY --from=ingressdataimage /build-output/ingress/nginx-ingress-controller /
RUN chmod +x /nginx-ingress-controller

COPY --from=ingressdataimage /build-output/authbind /bin/
RUN chmod +x /bin/authbind

COPY --from=dumbinitdataimage /build-output/dumb-init /dumb-init
RUN chmod +x /dumb-init

COPY --from=nginxdataimage /build-output/nginx-1.13.9-1.ngx.x86_64.rpm /nginx-1.13.9-1.ngx.x86_64.rpm

RUN yum update -y && yum install -y /nginx-1.13.9-1.ngx.x86_64.rpm

RUN mkdir -vp /etc/nginx/template /etc/nginx/geoip /ingress-controller
ADD rootfs/etc/nginx/template/nginx.tmpl /etc/nginx/template/
ADD rootfs/ingress-controller/* /ingress-controller/
ADD rootfs/etc/nginx/nginx.conf /etc/nginx/

ENTRYPOINT ["/dumb-init"]
CMD ["/nginx-ingress-controller"]

