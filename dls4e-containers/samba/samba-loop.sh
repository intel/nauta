#!/bin/bash -e
set -e

while true; do
  /bin/samba-create.sh || echo "Samba creation loop failed"
  sleep 2
done
