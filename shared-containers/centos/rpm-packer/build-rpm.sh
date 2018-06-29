#!/usr/bin/bash

set -e

PACKAGE_NAME=$1
PACKAGE_OUTPUT_DIR=$2

DIR=/root/rpmbuild

SPEC_DIR=${DIR}/SPECS
RPM=${DIR}/RPMS/x86_64/dls4e-${PACKAGE_NAME}-${RPM_VERSION}-${RPM_RELEASE}.x86_64.rpm

stat ${SPEC_DIR}/${PACKAGE_NAME}.spec

rpmbuild -bb --define "_dls4e_version ${RPM_VERSION}" --define "_dls4e_release ${RPM_RELEASE}" ${SPEC_DIR}/${PACKAGE_NAME}.spec

stat ${RPM}

cp ${RPM} ${PACKAGE_OUTPUT_DIR}
