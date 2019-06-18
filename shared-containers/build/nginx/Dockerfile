ARG BASE_IMAGE
FROM ${BASE_IMAGE}

RUN mkdir -p /build-output/ \
             /build && \
    yum update -y && \ 
    yum install -y rpm-build gcc make openssl-devel redhat-lsb-core && \
    yum clean all

COPY nginx-1.15.9-1.el7_4.ngx.src.rpm /build

WORKDIR /build
RUN rpmbuild --rebuild nginx-1.15.9-1.el7_4.ngx.src.rpm
RUN cp /root/rpmbuild/RPMS/x86_64/* /build-output/

