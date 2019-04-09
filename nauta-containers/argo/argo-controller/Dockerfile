ARG ARGO_IMAGE
ARG BASE_IMAGE=centos:7.6.1810

FROM ${ARGO_IMAGE} as argo-build
FROM ${BASE_IMAGE}

COPY --from=argo-build /build/work/src/github.com/argoproj/argo/dist/workflow-controller /bin/
ENTRYPOINT [ "workflow-controller" ]
