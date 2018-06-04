#!/bin/bash -x


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

/usr/sbin/nmbd      -F -S --debuglevel=${SAMBA_LOG_LEVEL}  &
#                    ^  ^
#                    |  |
# run in foreground -/  |
#                       |
#        log to stdout -/
#

sleep inf
