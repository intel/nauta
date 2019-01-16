#!/bin/bash -x
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



mkdir -vp /mnt/shared
chown nobody:nobody /mnt/shared
chmod 2777 /mnt/shared

# log level/verbosity: 0..10
SAMBA_LOG_LEVEL=${SAMBA_LOG_LEVEL:-3}

/bin/samba-loop.sh &

/usr/sbin/smbd      -F -S --debuglevel=${SAMBA_LOG_LEVEL}  &
#                    ^  ^
#                    |  |
# run in foreground -/  |
#                       |
#        log to stdout -/
#

# probably not needed for now:
#/usr/sbin/nmbd      -F -S --debuglevel=${SAMBA_LOG_LEVEL}  &
#                    ^  ^
#                    |  |
# run in foreground -/  |
#                       |
#        log to stdout -/
#

sleep inf
