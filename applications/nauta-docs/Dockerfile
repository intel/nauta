ARG NGINX_IMAGE="nginx:1.13.9"
ARG BASE_IMAGE
FROM ${BASE_IMAGE}
FROM ubuntu:18.04
ARG DOCS_VERSION="develop"
COPY --from=0 /docs /docs
ADD ["./app/", "/app"]

RUN apt update && apt install wget -y
RUN wget -q -t 3 -O pandoc.deb https://github.com/jgm/pandoc/releases/download/2.6/pandoc-2.6-1-amd64.deb
RUN apt install ./pandoc.deb

RUN cd /docs && chmod +x /app/tools/convert_to_html.sh && /app/tools/convert_to_html.sh ${DOCS_VERSION}

RUN find /docs -name "*.md" -type f -delete && rm -rf /docs/tools

FROM ${NGINX_IMAGE}

COPY --from=1 /docs/user-guide /docs
COPY --from=1 /app/css /docs/css
COPY --from=1 /app/img /docs/img

ADD ["./nginx.conf", "/etc/nginx/nginx.conf"]
