#!/usr/bin/env sh

set -e

BINPATH=${BINDIR}/${DETECTED_OS_TYPE}/${DETECTED_OS_ARCH}

HELM=${BINPATH}/helm
KUBECTL=${BINPATH}/kubectl
LOADER=${BINPATH}/loader

if [ ! -f "${HELM}" ]; then
    >&2 echo "Unable to find helm binary in ${HELM}"
    exit 1
fi
chmod +x ${HELM}
${HELM} version -c > /dev/null

if [ ! -f "${KUBECTL}" ]; then
    >&2 echo "Unable to find kubectl binary in ${KUBECTL}"
    exit 1
fi
chmod +x ${KUBECTL}
${KUBECTL} version --client > /dev/null

if [ ! -f "${LOADER}" ]; then
    >&2 echo "Unable to find loeader binary in ${LOADER}"
    exit 1
fi
