ARG PYTORCH_IMAGE
ARG BASE_IMAGE

FROM ${PYTORCH_IMAGE} as pytorch-build
FROM ${BASE_IMAGE}

ENV PYTHONUNBUFFERED 1

RUN yum clean all && yum update -y && yum install -y gcc

COPY --from=pytorch-build /pytorch_build/vision/dist/torchvision-0.3.0a0*-cp36-cp36m-linux_x86_64.whl /bin/

COPY --from=pytorch-build /pytorch_build/pytorch/dist/torch-1.2.0a0*-cp36-cp36m-linux_x86_64.whl /bin/

ADD requirements.txt .

ENV LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/opt/rh/rh-python36/root/usr/lib/
RUN pip install --no-cache-dir mkl-include==2019.0 mkl==2019.0
RUN pip install --no-cache-dir --force-reinstall /bin/torch-1.2.0a0*-cp36-cp36m-linux_x86_64.whl /bin/torchvision-0.3.0a0*-cp36-cp36m-linux_x86_64.whl && pip install --no-binary=:all: --no-cache-dir -r requirements.txt
