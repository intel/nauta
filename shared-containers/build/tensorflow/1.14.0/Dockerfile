ARG BASE_IMAGE
FROM ${BASE_IMAGE}

ENV BAZEL_VERSION 0.24.1
WORKDIR /
RUN source /opt/rh/devtoolset-8/enable && mkdir /bazel && \
    cd /bazel && \
    curl -H "User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36" -fSsL -O https://github.com/bazelbuild/bazel/releases/download/$BAZEL_VERSION/bazel-$BAZEL_VERSION-installer-linux-x86_64.sh && \
    curl -H "User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36" -fSsL -o /bazel/LICENSE.txt https://raw.githubusercontent.com/bazelbuild/bazel/master/LICENSE && \
    chmod +x bazel-*.sh && \
    ./bazel-$BAZEL_VERSION-installer-linux-x86_64.sh && \
    cd / && \
    rm -f /bazel/bazel-$BAZEL_VERSION-installer-linux-x86_64.sh

ENV TENSORFLOW_VERSION=1.14.0
 
ADD tensorflow-v${TENSORFLOW_VERSION}.tar.gz /tensorflow

WORKDIR /tensorflow/tensorflow-${TENSORFLOW_VERSION}/
ENV CC=gcc --std=c11 \
    CFLAGS=--std=c11
RUN source /opt/rh/devtoolset-8/enable && yes "" | ${PYTHON} configure.py
RUN source /opt/rh/devtoolset-8/enable && bazel build \
      --config=mkl \
      --cxxopt=-D_GLIBCXX_USE_CXX11_ABI=0 \
      --copt=-march=haswell \
      --copt=-mtune=broadwell \
      --copt=-O3 \
      --copt=-Wformat \
      --copt=-Wformat-security \
      --copt=-fstack-protector \
      --copt=-fPIC \
      --copt=-fpic \
      --linkopt=-znoexecstack \
      --linkopt=-zrelro \
      --linkopt=-znow \
      --linkopt=-fstack-protector \
      --linkopt=-pie \
      --jobs=8 \
      --local_resources=32000.0,16.0,1.0 \
      -c opt --verbose_failures //tensorflow/tools/pip_package:build_pip_package

RUN source /opt/rh/devtoolset-8/enable && bazel-bin/tensorflow/tools/pip_package/build_pip_package /build-output/
