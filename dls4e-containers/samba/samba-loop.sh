#!/bin/bash -e
set -e

function set_object_value() {
    kubectl patch u $1 --type merge --patch "{\"spec\":{\"$2\":\"$3\"}}"
}

function set_object_int_value() {
    kubectl patch u $1 --type merge --patch "{\"spec\":{\"$2\":$3}}"
}

function get_free_uid() {
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
  if ! id -u $kUID; then
      groupadd -g $kUID $USER
  fi
  if ! id $kUID; then
      useradd -u $kUID -g $kUID -m $USER
  fi
}

while true; do
    for user in `kubectl get u | cut -d ' ' -f 1 | grep -v NAME`; do
        STATE=`kubectl get u $user -o 'jsonpath={.spec.state}'`
        echo "User $user in state $STATE"
        echo "Creating user $user"
        PASSWORD=`kubectl get u $user -o 'jsonpath={.spec.password}'`
        if [ X"$PASSWORD" == X"" ]; then
            echo "Generating password"
            PASSWORD=`cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1`
            set_object_value $user password $PASSWORD
        fi
        kUID=`kubectl get u $user -o 'jsonpath={.spec.uid}'`
        if [ X"$kUID" == X"" ]; then
            echo "Generating UID"
            kUID=`get_free_uid`
            set_object_int_value $user uid $kUID
        fi
        create_user $user $kUID
        echo "Create input and output directories"
        mkdir -p /input/$user
        mkdir -p /output/$user

        chown -R $kUID:$kUID /input/$user /output/$user
        echo "Create links"
        ln -sfn /input/$user /home/$user/input
        ln -sfn /output/$user /home/$user/output
        if [ X"$STATE" != X"CREATED" ]; then
            echo "Update user state"
            set_object_value $user state CREATED
        fi
    done
    sleep 2
done
