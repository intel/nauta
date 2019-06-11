FROM ubuntu:18.04 as build

RUN apt-get update && apt-get install -y git

WORKDIR /root

RUN git clone https://github.com/opencv/dldt.git
WORKDIR /root/dldt
RUN git checkout 2018_R5
RUN mv model-optimizer /root

WORKDIR /root

RUN rm -rf dldt

FROM ubuntu:18.04

WORKDIR /root

RUN apt-get update && apt-get install -y sudo

COPY --from=build /root/model-optimizer /root/model-optimizer

WORKDIR /root/model-optimizer/install_prerequisites

RUN ./install_prerequisites_tf.sh
RUN ./install_prerequisites_onnx.sh

WORKDIR /root/model-optimizer
