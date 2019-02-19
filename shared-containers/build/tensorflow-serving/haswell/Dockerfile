ARG BASE_IMAGE
FROM ${BASE_IMAGE}
 
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
      -c opt --verbose_failures tensorflow_serving/...

RUN ln -sf bazel-serving-1.9.0 bazel-serving
RUN source /opt/rh/devtoolset-7/enable && bazel-bin/tensorflow_serving/tools/pip_package/build_pip_package /build-output/
RUN cp bazel-bin/tensorflow_serving/model_servers/tensorflow_model_server /build-output/tensorflow_model_server
