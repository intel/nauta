ARG BASE_IMAGE
FROM ${BASE_IMAGE}

RUN apt update
RUN apt install -y openjdk-11-jdk

ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64/

RUN mkdir -vp /build-output/ /build

COPY elasticsearch-6.4.0.tar.gz /build
COPY gradle.build.footer /build

WORKDIR /build
RUN tar -xvf /build/elasticsearch-6.4.0.tar.gz
WORKDIR /build/elasticsearch-6.4.0/

RUN cat /build/gradle.build.footer >> gradle.build

RUN ./gradlew -Dhttp.proxyHost=proxy-chain.intel.com -Dhttp.proxyPort=911 -Dhttps.proxyHost=proxy-chain.intel.com -Dhttps.proxyPort=911 cleanEclipse eclipse
RUN ./gradlew -Dhttp.proxyHost=proxy-chain.intel.com -Dhttp.proxyPort=911 -Dhttps.proxyHost=proxy-chain.intel.com -Dhttps.proxyPort=911 assemble

RUN mkdir -vp /build-output/sources
RUN find / -iname '*sources.jar' -exec cp {} /build-output/sources/ \;

RUN cp -vR ./distribution/* /build-output/


