ARG BASE_IMAGE
FROM ${BASE_IMAGE}

RUN mkdir -vp /build/gopath/
RUN mkdir -vp /build-output/ingress
ENV GOPATH=/build/gopath
WORKDIR /build/gopath

RUN mkdir -vp /build/gopath/src/k8s.io
RUN git clone https://github.com/kubernetes/ingress-nginx.git /build/gopath/src/k8s.io/ingress-nginx
RUN cd /build/gopath/src/k8s.io/ingress-nginx && git checkout 734361d58ae0ae8a685ccf23642c4dc703da9e86

RUN cd /build/gopath/src/k8s.io/ingress-nginx && make build
RUN find /tmp -iname nginx-ingress-controller -exec cp {} /build-output/ingress/  \;

RUN cd /build/gopath/src/k8s.io/ingress-nginx/images/404-server && CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -a -installsuffix cgo -ldflags '-w -s' -o /build-output/ingress/server

RUN mkdir -vp /build/authbind
WORKDIR /build/authbind
COPY authbind_2.1.2.tar.gz /build/authbind/
RUN tar -xf authbind_2.1.2.tar.gz
WORKDIR /build/authbind/authbind
RUN make
RUN cp authbind /build-output/

RUN cd /build-output && \
    tar -I pigz -cvf addons.tar.gz ingress authbind

