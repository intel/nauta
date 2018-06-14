#!/bin/bash
# INTEL CONFIDENTIAL
# Copyright (c) 2018 Intel Corporation

# The source code contained or described herein and all documents related to
# the source code ("Material") are owned by Intel Corporation or its suppliers
# or licensors. Title to the Material remains with Intel Corporation or its
# suppliers and licensors. The Material contains trade secrets and proprietary
# and confidential information of Intel or its suppliers and licensors. The
# Material is protected by worldwide copyright and trade secret laws and treaty
# provisions. No part of the Material may be used, copied, reproduced, modified,
# published, uploaded, posted, transmitted, distributed, or disclosed in any way
# without Intel's prior express written permission.

# No license under any patent, copyright, trade secret or other intellectual
# property right is granted to or conferred upon you by disclosure or delivery
# of the Materials, either expressly, by implication, inducement, estoppel or
# otherwise. Any license under such intellectual property rights must be express
# and approved by Intel in writing.

min_code_coverage=30

go test -coverprofile=cmd_cov.dat ./cmd/...
cmd_coverage=`go tool cover -func=cmd_cov.dat | grep total | awk -F' '  '{print $NF}'`
rm cmd_cov.dat

go test -coverprofile=pkg_cov.dat ./pkg/...
pkg_coverage=`go tool cover -func=pkg_cov.dat | grep total | awk -F' '  '{print $NF}'`
rm pkg_cov.dat

echo 'Code coverage:'
echo 'cmd module : ' $cmd_coverage
echo 'pkg module : ' $pkg_coverage

if (( $(awk 'BEGIN {print ("'$cmd_coverage'" < "'$min_code_coverage'")}') || 
      $(awk 'BEGIN {print ("'$pkg_coverage'" < "'$min_code_coverage'")}') )); then
  echo 'Code coverage is too low'
  exit 1
fi
