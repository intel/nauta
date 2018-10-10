#!/bin/bash -e
set -e

function delete_pv() {
    USER=$1
    INPUT_HOME_NAME=${APP_RELEASE}-${USER}-input-home
    INPUT_PUB_NAME=${APP_RELEASE}-${USER}-input-public

    OUTPUT_HOME_NAME=${APP_RELEASE}-${USER}-output-home
    OUTPUT_PUB_NAME=${APP_RELEASE}-${USER}-output-public

    kubectl delete pv $INPUT_HOME_NAME $INPUT_PUB_NAME $OUTPUT_HOME_NAME $OUTPUT_PUB_NAME
}

function delete_user() {
    USER=$1
    USER="${USER:1:${#USER}-2}"
    # check whether a user still exists in the system - at this moment this user
    # no longer exists in k8s cluster
    `id $USER >/dev/null 2>&1`

    if [ $? -eq 0 ];
    then
        echo "Deleting user $USER"
        # delete samba users
        smbpasswd -x $USER
        # remove pv
        delete_pv $USER
        # delete user
        userdel -r $USER
        # remove item in queue of users to be deleted
        kubectl patch configmap dls4enterprise-user-del --type=json -p="[{\"op\": \"remove\", \"path\": \"/data/$USER\"}]" -n dls4e
    else
        echo "User $USER not found"
    fi
}

USERS_TO_BE_DELETED=`kubectl get cm dls4enterprise-user-del -n dls4e -o=json | jq -r '.data'`

if [[ $USERS_TO_BE_DELETED != 'null' ]];
then
    for USER in `echo $USERS_TO_BE_DELETED | jq 'keys[]'`
    do
        echo "Deleting $USER"
        delete_user "$USER" || echo " An error occured during removal!"
    done
fi
