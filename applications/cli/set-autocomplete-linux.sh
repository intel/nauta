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

# autocomplete for dlsctl application

LICENSE_ACCEPTANCE_TEXT='DO NOT ACCESS, COPY OR PERFORM ANY PORTION OF THE PRE-RELEASE SOFTWARE
UNTIL YOU HAVE READ AND ACCEPTED THE TERMS AND CONDITIONS OF THIS
AGREEMENT LICENSE.TXT . BY COPYING, ACCESSING, OR PERFORMING
THE PRE-RELEASE SOFTWARE, YOU AGREE TO BE LEGALLY BOUND BY THE TERMS AND
CONDITIONS OF THIS AGREEMENT. Agree? (y/n)'

validate_dlsctl_home_config_directory() {
    local dlsctl_home_config_directory="$1"
    if [ -d "${dlsctl_home_config_directory}" ]; then
        # check if it is actual config directory of dlsctl - it should contain draft and helm binaries
        if [ -f "${dlsctl_home_config_directory}/draft" ] && [ -f "${dlsctl_home_config_directory}/helm" ]; then
            return 0
        else
            return 1
        fi
    else
        return 1
    fi
}

get_dlsctl_config_directory() {
    if [ -z "${DLS_CTL_CONFIG}" ]; then
        # DLS_CTL_CONFIG environment variable is not set
        local dlsctl_home_config_directory="${HOME}/config"
        if validate_dlsctl_home_config_directory "${dlsctl_home_config_directory}"; then
            echo "${dlsctl_home_config_directory}"
        else
            # get config path relative to autocomplete script
            local dlsctl_relative_config_directory="$(dirname "$0")/config"
            if [ -d "$dlsctl_relative_config_directory" ]; then
                echo "${dlsctl_relative_config_directory}"
            else
                # Unable to determine config directory path
                echo ''
            fi
        fi
    else
        # DLS_CTL_CONFIG environment variable is set
        echo "${DLS_CTL_CONFIG}"
    fi
}

check_license() {
    local dlsctl_config_directory
    dlsctl_config_directory=$(get_dlsctl_config_directory)

    if [ -z "${dlsctl_config_directory}" ]; then
        echo 'Unable to determine dlsctl config directory.'
        echo 'Please set dlsctl config directory path as a value of DLS_CTL_CONFIG environment variable.'
        exit 1
    fi

    local license_file="${dlsctl_config_directory}/license_accepted"
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

if grep -q "_DLSCTL_COMPLETE" ~/.bashrc; then
    echo 'Autocompletion for dlsctl application has been already set up.'
    exit 1
fi

FILE=$(realpath dlsctl)

echo -e '\n' >> ~/.bashrc
echo '# autocomplete for dlsctl application' >> ~/.bashrc
echo 'eval "$(_DLSCTL_COMPLETE=source '${FILE}')"' >> ~/.bashrc
