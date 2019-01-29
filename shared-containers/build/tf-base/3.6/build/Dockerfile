ARG BASE_IMAGE
FROM ${BASE_IMAGE}

RUN yum update -y
RUN yum install -y which
RUN yum install -y devtoolset-7-gcc*
RUN source /opt/rh/devtoolset-7/enable && gcc --version
RUN yum install -y --nogpgcheck curl git rsync unzip zip which \
                                java-1.8.0-openjdk-devel java-1.8.0-openjdk libpng12-devel \
                                pkg-config freetype-devel hdf5-devel libcurl patch \
                                make libtool automake

RUN mkdir /tensorflow /build-output -p

ENV PYTHON=python3.6
ENV PIP=pip3.6

RUN source /opt/rh/devtoolset-7/enable && ${PIP} install -U pip==19.0.* setuptools==40.6.*

RUN source /opt/rh/devtoolset-7/enable && ${PIP} install \
        Pillow==5.4.* \
        h5py==2.9.* \
        ipykernel==5.1.* \
        jupyter==1.0.* \
        matplotlib==3.0.* \
        mock==2.0.* \
        numpy==1.16.* \
        scipy==1.2.* \
        scikit-learn==0.20.* \
        pandas==0.23.* \
        wheel==0.32.*

RUN source /opt/rh/devtoolset-7/enable && ${PYTHON} -m ipykernel.kernelspec

RUN echo "startup --batch" >>/etc/bazel.bazelrc
RUN echo "build --spawn_strategy=standalone --genrule_strategy=standalone"  >>/etc/bazel.bazelrc

ENV BAZEL_VERSION 0.11.0
WORKDIR /
RUN source /opt/rh/devtoolset-7/enable && mkdir /bazel && \
    cd /bazel && \
    curl -H "User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36" -fSsL -O https://github.com/bazelbuild/bazel/releases/download/$BAZEL_VERSION/bazel-$BAZEL_VERSION-installer-linux-x86_64.sh && \
    curl -H "User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36" -fSsL -o /bazel/LICENSE.txt https://raw.githubusercontent.com/bazelbuild/bazel/master/LICENSE && \
    chmod +x bazel-*.sh && \
    ./bazel-$BAZEL_VERSION-installer-linux-x86_64.sh && \
    cd / && \
    rm -f /bazel/bazel-$BAZEL_VERSION-installer-linux-x86_64.sh

#RUN ln -fs /usr/bin/${PYTHON} /usr/bin/python
RUN ln -fs /opt/rh/rh-python36/root/usr/bin/${PYTHON} /usr/bin/python
