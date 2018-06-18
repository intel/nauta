#!/usr/bin/bash

set -e

SERVICE=$1
SRC=$2
DST=$3

PORT=$(kubectl -n dls4e get svc ${SERVICE} -o 'jsonpath={.spec.ports[?(.name=="dls4e")].nodePort}')

docker pull 127.0.0.1:${PORT}/${SRC}

docker tag 127.0.0.1:${PORT}/${SRC} 127.0.0.1:${PORT}/${DST}

docker push 127.0.0.1:${PORT}/${DST}
