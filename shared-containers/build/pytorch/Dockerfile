ARG BASE_IMAGE
FROM ${BASE_IMAGE}

RUN yum clean all && yum update -y && yum install -y bzip2 which gcc gcc-c++ openssl make git

RUN cd /tmp && curl -O https://repo.anaconda.com/miniconda/Miniconda2-4.6.14-Linux-x86_64.sh && bash Miniconda2-4.6.14-Linux-x86_64.sh -b

ENV PATH=$PATH:/root/miniconda2/bin/

RUN conda install -y numpy ninja pyyaml mkl mkl-include setuptools cmake cffi typing

WORKDIR /pytorch_build

ADD pytorch_sources_v1.2.0.tar.gz .

ENV PYTHONUNBUFFERED 1

RUN cd pytorch && pip3 install --no-binary=:all: --no-cache-dir -r requirements.txt && pip3 install setuptools wheel && python3 setup.py bdist_wheel

RUN pip3 install --no-cache-dir --force-reinstall /pytorch_build/pytorch/dist/torch-1.2.0a0*-cp36-cp36m-linux_x86_64.whl

ADD torchvision_sources_v0.3.0.tar.gz .

RUN cd vision && python3 setup.py bdist_wheel

RUN cp /pytorch_build/vision/dist/torchvision-0.3.0a0*-cp36-cp36m-linux_x86_64.whl /root
