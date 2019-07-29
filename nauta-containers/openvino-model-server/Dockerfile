ARG BASE_IMAGE
FROM ${BASE_IMAGE} as DEV

RUN mkdir /app

WORKDIR /app

ADD openvino-model-server.tar.gz .

WORKDIR /app/OpenVINO-model-server-master

RUN yum -y install autoconf \
                    automake \
                    build-essential \
                    ca-certificates \
                    curl \
                    gcc \
                    gcc-plugin-devel \
                    gcc-objc \
                    gcc-objc++ \
                    git \
                    gcc-c++ \
                    gstreamer1-plugins-base \
                    boost-regex \
                    boost-devel \
                    cairo-devel \
                    libgfortran \
                    glib2-devel \
                    libtool \
                    gstreamer1 \
                    gtk2-devel \
                    blas-devel \
                    pango-devel \
                    libpng12-devel \
                    openssl-libs \
                    libgusb-devel \
                    libusb \
                    pkgconfig \
                    unzip \
                    vim \
                    make \
                    wget && yum clean all

RUN wget https://cmake.org/files/v3.14/cmake-3.14.3.tar.gz && \
    tar -xvzf cmake-3.14.3.tar.gz && \
    cd cmake-3.14.3/  && \
    ./configure && \
    make -j$(nproc) && \
    make install

RUN pip3 install cython numpy
ARG DLDT_DIR=/2019_R1.1
RUN git clone --depth=1 -b 2019_R1.1 https://github.com/opencv/dldt.git ${DLDT_DIR} && \
    cd ${DLDT_DIR} && git submodule init && git submodule update --recursive && \
    rm -Rf .git && rm -Rf model-optimizer

WORKDIR ${DLDT_DIR}
RUN curl -L https://github.com/intel/mkl-dnn/releases/download/v0.18/mklml_lnx_2019.0.3.20190220.tgz | tar -xz
WORKDIR ${DLDT_DIR}/inference-engine/build

RUN cmake -DGEMM=MKL -DMKLROOT=${DLDT_DIR}/mklml_lnx_2019.0.3.20190220 -DENABLE_MKL_DNN=ON -DTHREADING=OMP -DCMAKE_BUILD_TYPE=Release ..

RUN make -j$(nproc)

WORKDIR ${DLDT_DIR}/inference-engine/ie_bridges/python/build
RUN cmake -DInferenceEngine_DIR=${DLDT_DIR}/inference-engine/build -DPYTHON_EXECUTABLE=$(which python3) -DPYTHON_LIBRARY=/opt/rh/rh-python36/root/usr/lib64/libpython3.6m.so -DPYTHON_INCLUDE_DIR=/opt/rh/rh-python36/root/usr/include/python3.6m ${DLDT_DIR}/inference-engine/ie_bridges/python && \
    make -j$(nproc)


FROM ${BASE_IMAGE} as PROD

RUN yum -y install ca-certificates curl libgomp && yum clean all

ADD openvino-model-server.tar.gz /
RUN mv /OpenVINO-model-server-master /ie-serving-py
WORKDIR /ie-serving-py

RUN virtualenv -p python3 .venv && . .venv/bin/activate && pip3 install -r requirements.txt && pip3 install .

COPY --from=DEV /2019_R1.1/inference-engine/bin/intel64/Release/lib/*.so /usr/local/lib/
COPY --from=DEV /2019_R1.1/inference-engine/ie_bridges/python/bin/intel64/Release/python_api/python3.6/openvino/ /usr/local/lib/openvino/
COPY --from=DEV /2019_R1.1/mklml_lnx_2019.0.3.20190220/lib/lib*.so /usr/local/lib/

ENV PATH=/ie-serving-py/.venv/bin/:$PATH
ENV LD_LIBRARY_PATH=/usr/local/lib
ENV PYTHONPATH=/usr/local/lib


