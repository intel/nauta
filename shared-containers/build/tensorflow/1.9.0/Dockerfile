ARG BASE_IMAGE
FROM ${BASE_IMAGE}

ENV TENSORFLOW_VERSION=1.9.0
 
ADD tensorflow-v${TENSORFLOW_VERSION}.tar.gz /tensorflow

WORKDIR /tensorflow/tensorflow-${TENSORFLOW_VERSION}/

RUN source /opt/rh/devtoolset-7/enable && yes "" | ${PYTHON} configure.py
RUN source /opt/rh/devtoolset-7/enable && bazel build \
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
      --jobs=64 \
      -c opt --verbose_failures //tensorflow/tools/pip_package:build_pip_package

RUN source /opt/rh/devtoolset-7/enable && bazel-bin/tensorflow/tools/pip_package/build_pip_package /build-output/