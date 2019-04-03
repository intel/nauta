ARG NGINX_IMAGE="nginx:1.13.9"
ARG BASE_IMAGE
FROM ${BASE_IMAGE}
FROM ubuntu:18.04
ARG DOCS_VERSION="develop"
COPY --from=0 /docs /docs
ADD ["./app/", "/app"]

RUN apt update && apt install wget unzip python3 -y
RUN wget -q -t 3 -O pandoc.deb https://github.com/jgm/pandoc/releases/download/2.6/pandoc-2.6-1-amd64.deb && apt install ./pandoc.deb

RUN cd /tmp && wget -q -t 3 -O font.zip https://github.com/google/material-design-icons/releases/download/3.0.0/material-design-icons-3.0.0.zip \
    && unzip -q font.zip

RUN python3 /app/tools/generate_index.py --docs-directory /docs/user-guide > /docs/user-guide/menu.html
RUN cd /docs && chmod +x /app/tools/convert_to_html.sh && /app/tools/convert_to_html.sh ${DOCS_VERSION}
RUN find /docs -name "*.md" -type f -delete && rm -rf /docs/tools

RUN wget -q -t 3 -O /app/js/jquery.min.js https://code.jquery.com/jquery-3.3.0.min.js

FROM ${NGINX_IMAGE}

COPY --from=1 /docs/user-guide /docs
COPY --from=1 /app/js /docs/js
COPY --from=1 /app/css /docs/css
COPY --from=1 /app/img /docs/img
COPY --from=1 /tmp/material-design-icons-3.0.0/iconfont/* /docs/font/

ADD ["./nginx.conf", "/etc/nginx/nginx.conf"]
