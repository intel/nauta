ARG BASE_IMAGE
FROM ${BASE_IMAGE}

RUN mkdir -vp /build-output/ /build

RUN yum clean all && yum install -y rpm-build gcc make openssl-devel redhat-lsb-core
#                                                                     ^^^^^^^^^^^^
#                                                                          |
#                                                                    not distributed,
#                                                                image used only to rebuild rpm.

COPY nginx-1.13.9-1.el7_4.ngx.src.rpm /build

WORKDIR /build
RUN rpmbuild --rebuild nginx-1.13.9-1.el7_4.ngx.src.rpm

RUN cp /root/rpmbuild/RPMS/x86_64/* /build-output/


