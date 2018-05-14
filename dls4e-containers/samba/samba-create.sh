#!/bin/bash -e
set -e

mkdir -p /input/public
mkdir -p /output/public

chmod 0777 -R /input/public /output/public

for user in `kubectl get u | cut -d ' ' -f 1 | grep -v NAME`; do
    /bin/samba-create-user.sh $user && /bin/samba-create-pv.sh $user || echo "Unable to create user $user"
done

exit 0
