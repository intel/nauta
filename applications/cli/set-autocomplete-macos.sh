#!/usr/bin/env bash
#
# INTEL CONFIDENTIAL
# Copyright (c) 2018 Intel Corporation
#
# The source code contained or described herein and all documents related to
# the source code ("Material") are owned by Intel Corporation or its suppliers
# or licensors. Title to the Material remains with Intel Corporation or its
# suppliers and licensors. The Material contains trade secrets and proprietary
# and confidential information of Intel or its suppliers and licensors. The
# Material is protected by worldwide copyright and trade secret laws and treaty
# provisions. No part of the Material may be used, copied, reproduced, modified,
# published, uploaded, posted, transmitted, distributed, or disclosed in any way
# without Intel's prior express written permission.
#
# No license under any patent, copyright, trade secret or other intellectual
# property right is granted to or conferred upon you by disclosure or delivery
# of the Materials, either expressly, by implication, inducement, estoppel or
# otherwise. Any license under such intellectual property rights must be express
# and approved by Intel in writing.
#

# autocomplete for nctl application

LICENSE_ACCEPTANCE_TEXT='DO NOT ACCESS, COPY OR PERFORM ANY PORTION OF THE PRE-RELEASE SOFTWARE
UNTIL YOU HAVE READ AND ACCEPTED THE TERMS AND CONDITIONS OF THIS
AGREEMENT LICENSE.TXT . BY COPYING, ACCESSING, OR PERFORMING
THE PRE-RELEASE SOFTWARE, YOU AGREE TO BE LEGALLY BOUND BY THE TERMS AND
CONDITIONS OF THIS AGREEMENT. Agree? (y/n)'

validate_nctl_home_config_directory() {
    local nctl_home_config_directory="$1"
    if [ -d "${nctl_home_config_directory}" ]; then
        # check if it is actual config directory of nctl - it should contain draft and helm binaries
        if [ -f "${nctl_home_config_directory}/draft" ] && [ -f "${nctl_home_config_directory}/helm" ]; then
            return 0
        else
            return 1
        fi
    else
        return 1
    fi
}

get_nctl_config_directory() {
    if [ -z "${NCTL_CONFIG}" ]; then
        # NCTL_CONFIG environment variable is not set
        local nctl_home_config_directory="${HOME}/config"
        if validate_nctl_home_config_directory "${nctl_home_config_directory}"; then
            echo "${nctl_home_config_directory}"
        else
            # get config path relative to autocomplete script
            local nctl_relative_config_directory="$(dirname "$0")/config"
            if [ -d "$nctl_relative_config_directory" ]; then
                echo "${nctl_relative_config_directory}"
            else
                # Unable to determine config directory path
                echo ''
            fi
        fi
    else
        # NCTL_CONFIG environment variable is set
        echo "${NCTL_CONFIG}"
    fi
}

check_license() {
    local nctl_config_directory
    nctl_config_directory=$(get_nctl_config_directory)

    if [ -z "${nctl_config_directory}" ]; then
        echo 'Unable to determine nctl config directory.'
        echo 'Please set nctl config directory path as a value of NCTL_CONFIG environment variable.'
        exit 1
    fi

    local license_file="${nctl_config_directory}/license_accepted"
    if [ -f "${license_file}" ]; then
        return 0
    fi

    echo "${LICENSE_ACCEPTANCE_TEXT}"
    read answer
    if [ "$answer" == 'y' ] || [ "$answer" == 'Y' ]; then
        touch "${license_file}"
        return 0
    else
        return 1
    fi
}

if ! check_license; then
    exit 1
fi

if [ ! -f ~/.bash_profile ]; then
    touch ~/.bash_profile
fi

if grep -q "_NCTL_COMPLETE" ~/.bash_profile; then
    echo 'Autocompletion for nctl application has been already set up.'
    exit 1
fi

FILE=$(cd $(dirname "$0"); pwd)/nctl;

echo -e '\n' >> ~/.bash_profile
echo '# autocomplete for nctl application' >> ~/.bash_profile
echo 'eval "$(_NCTL_COMPLETE=source '${FILE}')"' >> ~/.bash_profile
