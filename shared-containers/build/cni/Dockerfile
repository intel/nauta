ARG BASE_IMAGE
FROM ${BASE_IMAGE}

COPY cni-plugins.tar.gz ./

ENV CNI_PLUGINS_GO_PATH=${GOPATH}/src/github.com/containernetworking/plugins

RUN mkdir ${CNI_PLUGINS_GO_PATH} -p && \
    tar -zxf cni-plugins.tar.gz -C ${CNI_PLUGINS_GO_PATH} --strip-components=1 && \
    (cd ${CNI_PLUGINS_GO_PATH} && ./build.sh)

RUN mkdir -p /build-output/cni-plugins && \
    cp ${CNI_PLUGINS_GO_PATH}/bin/* /build-output/cni-plugins/ && \
    cd /build-output && \
    tar -I pigz -cf cni-plugins.tar.gz cni-plugins/
