ARG BASE_IMAGE
FROM ${BASE_IMAGE}

RUN source /opt/rh/devtoolset-8/enable && \
    curl -o cmake-3.12.3.tar.gz https://cmake.org/files/v3.12/cmake-3.12.3.tar.gz && \
    tar zxvf cmake-3.* && \
    cd cmake-3.* && \
    ./bootstrap --prefix=/usr/local -- -DCMAKE_USE_OPENSSL=ON && \
    make -j$(nproc) && \
    make install

RUN source /opt/rh/devtoolset-8/enable && pip install --no-binary :all: --no-cache-dir -U pip==18.1

RUN source /opt/rh/devtoolset-8/enable && pip install --no-binary :all: --no-cache-dir ninja==1.9.0 \
                                                                                       cmake==3.13.2 \
                                                                                       pyyaml==5.1.1 \
                                                                                       cffi==1.12.3 \
                                                                                       typing==3.7.4

RUN source /opt/rh/devtoolset-8/enable && pip install --no-cache-dir mkl==2019.0 mkl-include==2019.0

WORKDIR /pytorch_build

ADD pytorch_sources_v1.2.0.tar.gz .

ENV PYTHONUNBUFFERED 1

RUN source /opt/rh/devtoolset-8/enable && cd pytorch && \
           pip install --no-binary=:all: --no-cache-dir -r requirements.txt && python setup.py bdist_wheel

RUN source /opt/rh/devtoolset-8/enable && pip install --no-cache-dir --force-reinstall /pytorch_build/pytorch/dist/torch-1.2.0a0*-cp27-cp27mu-linux_x86_64.whl

ADD torchvision_sources_v0.3.0.tar.gz .

ENV LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/lib/

RUN source /opt/rh/devtoolset-8/enable && cd vision && python setup.py bdist_wheel

RUN cp /pytorch_build/vision/dist/torchvision-0.3.0a0*-cp27-cp27mu-linux_x86_64.whl /root
