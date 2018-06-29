ARG BASE_IMAGE
FROM ${BASE_IMAGE}

ENV GCC_VERSION=7.2.0

ENV GCC_OPTIONS="--with-system-zlib --disable-multilib --enable-languages=c,c++"

RUN mkdir -p /gcc
WORKDIR /gcc

COPY gcc-${GCC_VERSION}.tar.gz ./gcc.tar.gz

RUN tar -zxf gcc.tar.gz && mkdir -p build && (cd build && ../gcc-${GCC_VERSION}/configure ${GCC_OPTIONS} && \
    make -j 32 && make install) && rm -rf /gcc

RUN ln -fs /usr/local/bin/g++ /usr/bin/g++ &&  ln -fs /usr/local/bin/gcc /usr/bin/gcc
