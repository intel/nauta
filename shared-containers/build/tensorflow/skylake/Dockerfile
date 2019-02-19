ARG BASE_IMAGE
FROM ${BASE_IMAGE}

RUN source /opt/rh/devtoolset-7/enable && yes "" | ${PYTHON} configure.py
RUN source /opt/rh/devtoolset-7/enable && bazel build \
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
 
RUN source /opt/rh/devtoolset-7/enable && bazel-bin/tensorflow/tools/pip_package/build_pip_package /build-output/
