FROM scratch as centos
ADD centos-docker.tar.xz /
RUN yum update -y && yum -y upgrade && yum clean all
RUN rm /usr/lib64/libicui18n.so.50*
FROM centos as build
RUN mkdir -vp /build
ADD icu4c-63_1-src.tgz /build
RUN yum install -y gcc gcc-c++ make
WORKDIR /build/icu/source
RUN mkdir -vp /build/inst
RUN ./runConfigureICU Linux/gcc --disable-renaming --prefix=/build/inst && gmake && gmake install
FROM scratch
COPY --from=centos / /
COPY --from=build /build/inst/ /usr/local/
CMD ["/bin/bash"]
