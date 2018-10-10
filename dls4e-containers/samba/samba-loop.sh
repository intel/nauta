#!/bin/bash -e

for (( ; ; )) ; do
    echo "Checking if max-user-id config map exists..."
    if kubectl --namespace=dls4e get configmap max-user-id ; then
        echo "OK: max-user-id config maps already exists."
        break
    fi    
    
    if kubectl --namespace=dls4e get configmap max-user-id 2>&1 | grep NotFound ; then
        echo "Missing max-user-id config map, creating..."
        kubectl --namespace=dls4e create configmap max-user-id --from-literal=max-user-id=9999
    fi
    if kubectl --namespace=dls4e get configmap max-user-id ; then
        echo "OK: max-user-id config maps was created."
        break
    fi
    sleep 5
done


FIRST_RUN=--init
while true; do
  /bin/samba-create.sh $FIRST_RUN || echo "Samba creation loop failed"
  /bin/samba-delete-users.sh
  FIRST_RUN=
  sleep 5
done

