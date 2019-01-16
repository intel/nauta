#!/usr/bin/bash
#
# Copyright (c) 2019 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


set -e

PACKAGE_NAME=$1
PACKAGE_OUTPUT_DIR=$2

DIR=/root/rpmbuild

SPEC_DIR=${DIR}/SPECS
RPM=${DIR}/RPMS/x86_64/nauta-${PACKAGE_NAME}-${RPM_VERSION}-${RPM_RELEASE}.x86_64.rpm

stat ${SPEC_DIR}/${PACKAGE_NAME}.spec

rpmbuild -bb --define "_nauta_version ${RPM_VERSION}" --define "_nauta_release ${RPM_RELEASE}" ${SPEC_DIR}/${PACKAGE_NAME}.spec

stat ${RPM}

cp ${RPM} ${PACKAGE_OUTPUT_DIR}
