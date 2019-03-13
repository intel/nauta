ARG BASE_IMAGE
FROM ${BASE_IMAGE}

RUN yum clean all && yum update -y && yum install rh-python36 -y

ENV PATH=$PATH:/opt/rh/rh-python36/root/usr/bin
ENV LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/opt/rh/rh-python36/root/usr/lib64
ENV MANPATH=$MANPATH:/opt/rh/rh-python36/root/usr/share/man
ENV PKG_CONFIG_PATH=$PKG_CONFIG_PATH:/opt/rh/rh-python36/root/usr/lib64/pkgconfig
ENV XDG_DATA_DIRS="${XDG_DATA_DIRS:-/usr/local/share:/usr/share}:/opt/rh/rh-python36/root/usr/share"

RUN pip3.6 install -U pip==19.0.3
