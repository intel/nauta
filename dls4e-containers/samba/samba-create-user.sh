#!/bin/bash -e
set -e

function set_object_value() {
    kubectl patch u $1 --type merge --patch "{\"spec\":{\"$2\":\"$3\"}}"
}

function set_object_int_value() {
    kubectl patch u $1 --type merge --patch "{\"spec\":{\"$2\":$3}}"
}

BLOCKED_USERNAMES="root admin centos samba"
function username_blocked() {
  for name in ${BLOCKED_USERNAMES}; do
    if [ X"$1" == X"${name}" ]; then
      return 1
    fi
  done
}

function get_free_uid() {
  if id $1 > /dev/null 2>&1; then
      id -u $1
      return
  fi
  for n in {10000..20000}; do
      if [ X"`kubectl get user -o "jsonpath={.items[?(@.spec.uid==\"$n\")]}"`" == X"" ]; then
          echo $n
          return
      fi
  done
}

function create_user() {
  USER=$1
  kUID=$2
  PASSWORD=$3
  if ! id -u $kUID; then
      groupadd -g $kUID $USER
  fi
  if ! id $kUID; then
      useradd -u $kUID -g $kUID -m $USER
  fi
  ( echo ${PASSWORD} ; echo ${PASSWORD}; ) | smbpasswd -a "${USER}"
}

user=$1
#if username_blocked ${user}; then
#  echo "User name ${name} is blocked"
#  exit 1
#fi

STATE=`kubectl get u $user -o 'jsonpath={.spec.state}'`
echo "User $user in state $STATE"
echo "Creating user $user"
if ! kubectl -n $user get secret password; then
echo """
apiVersion: v1
kind: Secret
metadata:
  name: password
  namespace: $user
data:
  password: `cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1 | base64 -w0`
""" | kubectl create -f -
fi
PASSWORD=`kubectl -n $user get secret password -o 'jsonpath={.data.password}' | base64 -d`
kUID=`kubectl get u $user -o 'jsonpath={.spec.uid}'`
if [ X"$kUID" == X"" ]; then
    echo "Generating UID"
    kUID=`get_free_uid $user`
    set_object_int_value $user uid $kUID
fi
create_user $user $kUID $PASSWORD
echo "Create input and output directories"
mkdir -p /input/$user
mkdir -p /output/$user

chown -R $kUID:$kUID /input/$user /output/$user

if [ X"$STATE" != X"CREATED" ]; then
    echo "Update user state"
    set_object_value $user state CREATED
fi

exit 0
