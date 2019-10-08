ARG TENSORFLOW_BUILD_IMAGE
ARG BASE_IMAGE=centos:7.6.1810
FROM ${TENSORFLOW_BUILD_IMAGE} as tfbuild
FROM ${BASE_IMAGE} as build

RUN yum update -y && yum install -y centos-release-scl && yum install -y git make devtoolset-7-gcc*

WORKDIR /root
# OpenVino model optimizer build
RUN git clone https://github.com/opencv/dldt.git
WORKDIR /root/dldt
RUN git checkout 2018_R5
RUN mv model-optimizer /root

# OpenVino dependency - onnx - build
WORKDIR /onnx_build

RUN source /opt/rh/devtoolset-7/enable && \
    curl -o cmake-3.12.3.tar.gz https://cmake.org/files/v3.12/cmake-3.12.3.tar.gz && \
    tar zxvf cmake-3.* && \
    cd cmake-3.* && \
    ./bootstrap --prefix=/usr/local && \
    make -j$(nproc) && \
    make install

RUN curl -L -o protobuf-3.6.1-4.el7.x86_64.rpm https://cbs.centos.org/kojifiles/packages/protobuf/3.6.1/4.el7/x86_64/protobuf-3.6.1-4.el7.x86_64.rpm
RUN curl -L -o protobuf-devel-3.6.1-4.el7.x86_64.rpm https://cbs.centos.org/kojifiles/packages/protobuf/3.6.1/4.el7/x86_64/protobuf-devel-3.6.1-4.el7.x86_64.rpm
RUN curl -L -o protobuf-compiler-3.6.1-4.el7.x86_64.rpm https://cbs.centos.org/kojifiles/packages/protobuf/3.6.1/4.el7/x86_64/protobuf-compiler-3.6.1-4.el7.x86_64.rpm

RUN  yum -y install protobuf-3.6.1-4.el7.x86_64.rpm protobuf-compiler-3.6.1-4.el7.x86_64.rpm protobuf-devel-3.6.1-4.el7.x86_64.rpm

RUN source /opt/rh/devtoolset-7/enable && pip3.6 install setuptools==40.8.0 wheel==0.31.1 && pip3.6 wheel --no-binary=:all: onnx

FROM ${BASE_IMAGE}

ENV TENSORFLOW_VERSION=1.14.0

WORKDIR /root

COPY --from=build /root/model-optimizer /root/model-optimizer
COPY --from=tfbuild /build-output/tensorflow-${TENSORFLOW_VERSION}-*.whl /
COPY --from=build /onnx_build/*.whl /

WORKDIR /root/model-optimizer

RUN pip install --no-binary=:all: --force-reinstall -U pip
RUN pip install --no-cache-dir --force-reinstall /*.whl && \
    pip install --no-binary=:all: --no-cache-dir -r requirements_tf.txt -r requirements_onnx.txt

RUN rm /*.whl
