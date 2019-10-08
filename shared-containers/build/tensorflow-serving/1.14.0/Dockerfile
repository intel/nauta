ARG BASE_IMAGE
FROM ${BASE_IMAGE}
ENV TENSORFLOW_SERVING_VERSION=1.14.0

ENV BAZEL_VERSION 0.24.1
WORKDIR /
RUN source /opt/rh/devtoolset-8/enable && mkdir /bazel && \
    cd /bazel && \
    curl -H "User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36" -fSsL -O https://github.com/bazelbuild/bazel/releases/download/$BAZEL_VERSION/bazel-$BAZEL_VERSION-installer-linux-x86_64.sh && \
    curl -H "User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36" -fSsL -o /bazel/LICENSE.txt https://raw.githubusercontent.com/bazelbuild/bazel/master/LICENSE && \
    chmod +x bazel-*.sh && \
    ./bazel-$BAZEL_VERSION-installer-linux-x86_64.sh

ADD tensorflow-serving-v${TENSORFLOW_SERVING_VERSION}.tar.gz /tensorflow
WORKDIR /tensorflow/serving-${TENSORFLOW_SERVING_VERSION}/

RUN source /opt/rh/devtoolset-8/enable && bazel build \
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
      --incompatible_disallow_data_transition=false \
      --jobs=8 \
      --local_resources=32000.0,16.0,1.0 \
      -c opt --verbose_failures tensorflow_serving/...

RUN ln -sf bazel-serving-1.9.0 bazel-serving
RUN source /opt/rh/devtoolset-8/enable && bazel-bin/tensorflow_serving/tools/pip_package/build_pip_package /build-output/
RUN cp bazel-bin/tensorflow_serving/model_servers/tensorflow_model_server /build-output/tensorflow_model_server
