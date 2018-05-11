#!/bin/bash -x


mkdir -vp /mnt/shared
chown nobody:nobody /mnt/shared
chmod 2777 /mnt/shared

/bin/samba-loop.sh &

/usr/sbin/smbd      -F -S  &
#                    ^  ^
#                    |  |
# run in foreground -/  |
#                       |
#        log to stdout -/
#

/usr/sbin/nmbd      -F -S  &
#                    ^  ^
#                    |  |
# run in foreground -/  |
#                       |
#        log to stdout -/
#

sleep inf
