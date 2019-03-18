FROM ubuntu:18.04
ARG DOCS_VERSION="develop"

RUN apt update && apt install wget -y
RUN wget -q -t 3 -O pandoc.deb https://github.com/jgm/pandoc/releases/download/2.6/pandoc-2.6-1-amd64.deb
RUN apt install ./pandoc.deb

ADD ["./", "/docs/"]

RUN cd /docs && chmod +x .utils/convert_to_html.sh && .utils/convert_to_html.sh $DOCS_VERSION

RUN find /docs -name "*.md" -type f -delete

FROM nginx:1.13.9

COPY --from=0 /docs/user-guide /docs
COPY --from=0 /docs/.utils/uikit.css /docs/uikit.css

RUN echo "user  nginx; \n\
           worker_processes  1; \n\
           error_log  /var/log/nginx/error.log warn; \n\
           pid        /var/run/nginx.pid; \n\
           events { \n\
               worker_connections  1024; \n\
           } \n\
           http { \n\
               include       /etc/nginx/mime.types; \n\
               default_type  application/octet-stream; \n\
               log_format  main  '$remote_addr - $remote_user [$time_local] \"$request\" ' \n\
                                 '$status $body_bytes_sent \"$http_referer\" ' \n\
                                 '\"$http_user_agent\" \"$http_x_forwarded_for\"'; \n\
               access_log  /var/log/nginx/access.log  main; \n\
               sendfile        on; \n\
               keepalive_timeout  65; \n\
               server { \n\
                   listen 0.0.0.0:80; \n\
                   server_name _; \n\
                   location / { \n\
                       root /docs; \n\
                       index README.html; \n\
                   } \n\
               } \n\
           }" \
           > /etc/nginx/nginx.conf
