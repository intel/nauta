#!/usr/bin/env bash
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

if [ ! -f ~/.bashrc ]; then
    touch ~/.bashrc
fi

if grep -q "_NCTL_COMPLETE" ~/.bashrc; then
    echo 'Autocompletion for nctl application has been already set up.'
    exit 1
fi

FILE=$(realpath nctl)

echo -e '\n' >> ~/.bashrc
echo '# autocomplete for nctl application' >> ~/.bashrc
echo 'eval "$(_NCTL_COMPLETE=source '${FILE}')"' >> ~/.bashrc
