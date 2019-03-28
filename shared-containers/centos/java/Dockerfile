ARG BASE_IMAGE
FROM ${BASE_IMAGE}

RUN yum update -y && yum autoremove default-jre && yum clean all
ADD openjdk-11.0.2_linux-x64_bin.tar.gz /usr/lib/jvm
ENV JAVA_HOME=/usr/lib/jvm/jdk-11.0.2 \
    PATH=${JAVA_HOME}/bin:${PATH}
