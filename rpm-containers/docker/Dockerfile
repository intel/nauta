FROM centos:7.4.1708

WORKDIR /out

RUN curl https://download.docker.com/linux/centos/7/x86_64/stable/Packages/docker-ce-18.06.0.ce-3.el7.x86_64.rpm -o docker-ce-18.06.0.ce-3.el7.x86_64.rpm
RUN curl https://download.docker.com/linux/centos/7/debug-x86_64/edge/Packages/docker-ce-debuginfo-18.06.0.ce-3.el7.x86_64.rpm -o docker-ce-debuginfo-18.06.0.ce-3.el7.x86_64.rpm
RUN yumdownloader container-selinux-2.68-1.el7
