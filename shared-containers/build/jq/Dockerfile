ARG BASE_IMAGE
FROM ${BASE_IMAGE}

RUN ln -s /usr/share/aclocal /usr/local/share/aclocal

RUN mkdir -vp /build-output/ /build

COPY automake-1.14.tar.gz /build
WORKDIR /build
RUN tar -xvf /build/automake-1.14.tar.gz
WORKDIR /build/automake-1.14/
RUN ./configure --prefix /usr
RUN make install

COPY jq-1.6.tar.gz /build

WORKDIR /build
RUN tar -xvf /build/jq-1.6.tar.gz
WORKDIR /build/jq/
RUN autoreconf -fi
RUN ./configure --with-oniguruma=builtin
RUN make -j8

RUN cp jq /build-output/jq


