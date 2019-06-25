FROM scratch as centos

ADD centos-docker.tar.xz /
ADD os.repo /etc/yum.repos.d/

RUN yum-config-manager --disable "CentOS-7 - Updates" "CentOS-7 - Extras" "CentOS-7 - Base"
RUN yum update -y && yum -y upgrade && yum clean all

FROM centos as build

RUN mkdir -vp /build

ADD icu4c-63_1-src.tgz /build
RUN yum install -y gcc gcc-c++ make && yum clean all

WORKDIR /build/icu/source
RUN mkdir -vp /build/inst
RUN ./runConfigureICU Linux/gcc --disable-renaming --prefix=/build/inst && gmake && gmake install
FROM scratch
COPY --from=centos / /
COPY --from=build /build/inst/ /usr/local/
CMD ["/bin/bash"]
