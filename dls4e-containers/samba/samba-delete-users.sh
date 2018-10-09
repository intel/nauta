#!/bin/bash -e
set -e

function delete_user() {
  USER=$1

  echo "Deleting user $USER"
  userdel -r $USER

  echo "Deleting group"
  groupdel $USER
}