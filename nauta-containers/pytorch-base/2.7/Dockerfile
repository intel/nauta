ARG PYTORCH_IMAGE
ARG BASE_IMAGE
ARG METRICS_IMAGE

FROM ${PYTORCH_IMAGE} as pytorch-build
FROM ${METRICS_IMAGE} as metrics
FROM ${BASE_IMAGE}

ENV PYTHONUNBUFFERED 1

RUN yum clean all && yum update -y && yum install -y gcc

COPY --from=pytorch-build /pytorch_build/vision/dist/torchvision-0.3.0a0*-cp27-cp27mu-linux_x86_64.whl /bin/

COPY --from=pytorch-build /pytorch_build/pytorch/dist/torch-1.2.0a0*-cp27-cp27mu-linux_x86_64.whl /bin/

ADD requirements.txt .

COPY --from=pytorch-build /usr/lib/libmkl* /opt/rh/rh-python36/root/usr/lib/

COPY --from=pytorch-build /usr/lib64/libopenblas* /opt/rh/rh-python36/root/usr/lib/
COPY --from=pytorch-build /usr/lib64/libgf* /opt/rh/rh-python36/root/usr/lib/
COPY --from=pytorch-build /usr/lib64/libquadmath* /opt/rh/rh-python36/root/usr/lib/

COPY --from=metrics /build-output/experiment_metrics-*.tar.gz /

RUN pip install --ignore-installed --no-cache-dir /experiment_metrics-*.tar.gz

ENV LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/opt/rh/rh-python36/root/usr/lib/
RUN pip install --no-cache-dir mkl-include==2019.0 mkl==2019.0 && pip install --no-binary=:all: --no-cache-dir -r requirements.txt && pip install --no-cache-dir --force-reinstall /bin/torch-1.2.0a0*-cp27-cp27mu-linux_x86_64.whl /bin/torchvision-0.3.0a0*-cp27-cp27mu-linux_x86_64.whl
