ARG BASE_IMAGE
FROM ${BASE_IMAGE}

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        git \
        libcurl3-dev \
        libfreetype6-dev \
        libhdf5-serial-dev \
        libpng12-dev \
        libzmq3-dev \
        pkg-config \
        python-dev \
        python3-dev \
        python3-pip \
        rsync \
        software-properties-common \
        unzip \
        zip \
        zlib1g-dev \
        openjdk-8-jdk \
        openjdk-8-jre-headless \
        && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir /tensorflow /build-output -p

ENV PYTHON=python3
ENV PIP=pip3
ENV TENSORFLOW_VERSION=1.9.0

RUN ${PIP} install -U pip setuptools

RUN ${PIP} install \
        Pillow \
        h5py \
        ipykernel \
        jupyter \
        matplotlib \
        mock \
        numpy \
        scipy \
        sklearn \
        pandas \
        wheel

RUN ${PYTHON} -m ipykernel.kernelspec

RUN echo "startup --batch" >>/etc/bazel.bazelrc
RUN echo "build --spawn_strategy=standalone --genrule_strategy=standalone"  >>/etc/bazel.bazelrc

ENV BAZEL_VERSION 0.11.0
WORKDIR /
RUN mkdir /bazel && \
    cd /bazel && \
    curl -H "User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36" -fSsL -O https://github.com/bazelbuild/bazel/releases/download/$BAZEL_VERSION/bazel-$BAZEL_VERSION-installer-linux-x86_64.sh && \
    curl -H "User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36" -fSsL -o /bazel/LICENSE.txt https://raw.githubusercontent.com/bazelbuild/bazel/master/LICENSE && \
    chmod +x bazel-*.sh && \
    ./bazel-$BAZEL_VERSION-installer-linux-x86_64.sh && \
    cd / && \
    rm -f /bazel/bazel-$BAZEL_VERSION-installer-linux-x86_64.sh

ADD tensorflow-v${TENSORFLOW_VERSION}.tar.gz /tensorflow

WORKDIR /tensorflow/tensorflow-${TENSORFLOW_VERSION}/

RUN yes "" | ${PYTHON} configure.py
RUN bazel build \
        --cxxopt=-D_GLIBCXX_USE_CXX11_ABI=0 \
        --copt=-march=broadwell \
        --copt=-mclflushopt \
        --copt=-mxsavec \
        --copt=-mxsaves \
        --copt=-mavx512f \
        --copt=-mavx512vl \
        --copt=-mavx512bw \
        --copt=-mavx512dq \
        --copt=-mavx512cd \
        --copt=-O3 \
        --config=mkl \
        --jobs=64 \
        -c opt --verbose_failures //tensorflow/tools/pip_package:build_pip_package

RUN bazel-bin/tensorflow/tools/pip_package/build_pip_package /build-output/
