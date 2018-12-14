FROM nginx:1.13.9

RUN mkdir /docs

ADD ["./", "/docs/"]

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
                       index Default.htm; \n\
                   } \n\
               } \n\
           }" \
           > /etc/nginx/nginx.conf
