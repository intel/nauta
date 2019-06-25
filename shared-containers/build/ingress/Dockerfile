ARG BASE_IMAGE
FROM ${BASE_IMAGE}

RUN mkdir -vp /build/gopath/ \
              /build-output/ingress \
              /build/gopath/src/k8s.io \
              /build/authbind

ENV GOPATH=/build/gopath

WORKDIR /build/gopath

RUN git clone https://github.com/kubernetes/ingress-nginx.git /build/gopath/src/k8s.io/ingress-nginx && \
    cd /build/gopath/src/k8s.io/ingress-nginx && git checkout 734361d58ae0ae8a685ccf23642c4dc703da9e86 && \
    cd /build/gopath/src/k8s.io/ingress-nginx && make build && \
    find /tmp -iname nginx-ingress-controller -exec cp {} /build-output/ingress/  \; && \
    cd /build/gopath/src/k8s.io/ingress-nginx/images/404-server && CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -a -installsuffix cgo -ldflags '-w -s' -o /build-output/ingress/server && \
    rm -rf /build/gopath/src/k8s.io 
    
ADD authbind_2.1.2.tar.gz /build/

WORKDIR /build/authbind

RUN make && \
    cp authbind /build-output/ && cd /build-output && \
    tar -I pigz -cvf addons.tar.gz ingress authbind && rm -rf /build/authbind
