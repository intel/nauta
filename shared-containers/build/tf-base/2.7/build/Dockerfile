ARG BASE_IMAGE
FROM ${BASE_IMAGE}

RUN yum update -y && yum install -y which devtoolset-8-gcc*
RUN source /opt/rh/devtoolset-8/enable && gcc --version
RUN yum install -y --nogpgcheck curl git rsync unzip zip which \
                                java-1.8.0-openjdk-devel java-1.8.0-openjdk libpng-devel \
                                pkg-config freetype-devel hdf5-devel libcurl patch \
                                make libtool automake gcc-gfortran python2-devel openblas-devel \
                                lapack-devel Cython libjpeg-devel pkgconfig freetype-devel

RUN mkdir /tensorflow /build-output -p

ENV PYTHON=python2.7
ENV PIP=pip2.7

RUN source /opt/rh/devtoolset-8/enable && ${PIP} install --force-reinstall --no-binary :all: --no-clean -U setuptools==40.6.*
RUN source /opt/rh/devtoolset-8/enable && ${PIP} install --force-reinstall --no-binary :all: --no-clean -U pip==19.0.*
RUN source /opt/rh/devtoolset-8/enable && ${PIP} install --no-binary :all: --no-clean --ignore-installed scikit-build ptyprocess==0.5.2 MarkupSafe==1.1.1 numpy==1.16.*

RUN source /opt/rh/devtoolset-8/enable && ${PIP} install --ignore-installed nbconvert entrypoints

RUN source /opt/rh/devtoolset-8/enable && ${PIP} install --no-binary :all: --no-clean \
        Pillow==5.4.* \
        h5py==2.9.* \
        ipykernel==4.10.* \
        matplotlib==2.2.0 \
        jupyter==1.0.* \
        mock==2.0.* \
        scipy==1.2.* \
        scikit-learn==0.20.* \
        pandas==0.23.* \
        wheel==0.32.* \
        sklearn \
        tornado==4.5.3 \
        prompt-toolkit==1.0.15 \
        testpath==0.3.1 \
        terminado==0.6 \
        notebook==4.4.1 \
        keras-applications==1.0.7 \
        keras-preprocessing==1.0.9


RUN source /opt/rh/devtoolset-8/enable && ${PYTHON} -m ipykernel.kernelspec

RUN echo "startup --batch" >>/etc/bazel.bazelrc
RUN echo "build --spawn_strategy=standalone --genrule_strategy=standalone"  >>/etc/bazel.bazelrc

#ENV BAZEL_VERSION 0.21.0
#WORKDIR /
#RUN source /opt/rh/devtoolset-8/enable && mkdir /bazel && \
#    cd /bazel && \
#    curl -H "User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36" -fSsL -O https://github.com/bazelbuild/bazel/releases/download/$BAZEL_VERSION/bazel-$BAZEL_VERSION-installer-linux-x86_64.sh && \
#    curl -H "User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36" -fSsL -o /bazel/LICENSE.txt https://raw.githubusercontent.com/bazelbuild/bazel/master/LICENSE && \
#    chmod +x bazel-*.sh && \
#    ./bazel-$BAZEL_VERSION-installer-linux-x86_64.sh && \
#    cd / && \
#    rm -f /bazel/bazel-$BAZEL_VERSION-installer-linux-x86_64.sh

RUN ln -fs /usr/bin/${PYTHON} /usr/bin/python
