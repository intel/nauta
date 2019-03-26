ARG BASE_IMAGE
FROM ${BASE_IMAGE}

RUN apt -y update && apt autoremove default-jre

ADD openjdk-11.0.2_linux-x64_bin.tar.gz /usr/lib/jvm
RUN sh -c 'for bin in /usr/lib/jvm/jdk-11.0.2/bin/*; do update-alternatives --install /usr/bin/$(basename $bin) $(basename $bin) $bin 100; done'
RUN sh -c 'for bin in /usr/lib/jvm/jdk-11.0.2/bin/*; do update-alternatives --set $(basename $bin) $bin; done'

ENV JAVA_HOME=/usr/lib/jvm/jdk-11.0.2

RUN mkdir -vp /build-output/ /build

COPY elasticsearch-6.6.2.tar.gz /build
COPY gradle.build.footer /build

WORKDIR /build
RUN tar -xvf /build/elasticsearch-6.6.2.tar.gz
WORKDIR /build/elasticsearch-6.6.2/

RUN cat /build/gradle.build.footer >> gradle.build

RUN ./gradlew -Dhttp.proxyHost=proxy-chain.intel.com -Dhttp.proxyPort=911 -Dhttps.proxyHost=proxy-chain.intel.com -Dhttps.proxyPort=911 cleanEclipse eclipse
RUN ./gradlew -Dhttp.proxyHost=proxy-chain.intel.com -Dhttp.proxyPort=911 -Dhttps.proxyHost=proxy-chain.intel.com -Dhttps.proxyPort=911 assemble

RUN mkdir -vp /build-output/sources
RUN find / -iname '*sources.jar' -exec cp {} /build-output/sources/ \;

RUN cp -vR ./distribution/* /build-output/
