ARG BASE_IMAGE
FROM ${BASE_IMAGE}

RUN mkdir -vp /build-output/ /build

RUN yum clean all && yum install -y rpm-build gcc make openssl-devel redhat-lsb-core gcc-c++ bzip2
#                                                                     ^^^^^^^^^^^^
#                                                                          |
#                                                                    not distributed,
#                                                                image used only to rebuild rpm.

COPY node-v8.12.0.tar.gz /build

WORKDIR /build
RUN tar -xf node-v8.12.0.tar.gz
#WORKDIR /build/node-v8.12.0
RUN cd node-v8.12.0 && ./configure && make -j4 && make install && cd .. && rm -rf node-v8.12.0
#RUN make -j4
#RUN ls -lahR
#RUN make install
#RUN cp /root/rpmbuild/RPMS/x86_64/* /build-output/


