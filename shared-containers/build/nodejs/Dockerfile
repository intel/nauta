ARG BASE_IMAGE
FROM ${BASE_IMAGE}

RUN mkdir -vp /build-output/ /build

RUN yum update -y && yum install -y rpm-build gcc make openssl-devel redhat-lsb-core gcc-c++ bzip2 && yum clean all
#                                                                                    ^^^^^^^^^^^^
#                                                                                         |
#                                                                                  not distributed,
#                                                                            image used only to rebuild rpm.

COPY node-v8.12.0.tar.gz /build

WORKDIR /build
RUN tar -xf node-v8.12.0.tar.gz && cd node-v8.12.0 && ./configure && make -j4 && make install && cd .. && rm -rf node-v8.12.0
#RUN cp /root/rpmbuild/RPMS/x86_64/* /build-output/
