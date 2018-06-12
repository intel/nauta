#!/bin/bash -e
set -e

mkdir -p /input/public
mkdir -p /output/public

# chmod 0777 -R /input/public /output/public

function create_user() {
    echo "(Re)Creating user $1"
    /bin/samba-create-user.sh $1 && /bin/samba-create-pv.sh $1 || echo "Unable to create user $1"
}

ALL_USERS_JSON=`kubectl get u -o=json`
ALL_USERS_COUNT=`echo "${ALL_USERS_JSON}" | jq '.items | length'`

date
echo "Current user count: $ALL_USERS_COUNT"

for (( n = 0 ; n < $ALL_USERS_COUNT ; n++ )) ; do
    CURRENT_USER=`echo "$ALL_USERS_JSON" | jq ".items[$n]"`
    CURRENT_USER_NAME=`echo "$CURRENT_USER" | jq -r '.metadata.name'`
    CURRENT_USER_UID=`echo "$CURRENT_USER" | jq -r '.spec.uid'`
    CURRENT_USER_STATE=`echo "$CURRENT_USER" | jq -r '.spec.state'`
    echo "Found user: $CURRENT_USER_NAME, uid: $CURRENT_USER_UID, state: $CURRENT_USER_STATE"

    if [[ "x$1" == "x--init" ]] ; then
        echo " -> first run, creating user no matter of their reported state ($CURRENT_USER_STATE)"
        create_user $CURRENT_USER_NAME
    else
        if [[ "x$CURRENT_USER_STATE" != "xCREATED" ]] ; then
            create_user $CURRENT_USER_NAME
        else
            echo "User already exists, doing nothing."
            if [[ "x$CURRENT_USER_UID" == "x" ]] ; then
                echo "Warning: user doesn't have UID assigned"
            fi
        fi
    fi
done

