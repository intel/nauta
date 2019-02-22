#!/bin/bash -x
#
# Copyright (c) 2019 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


function create_user() {
  USER=$1
  kUID=$2
  PASSWORD=$3
  echo "Checking if group already exists $kUID ..."
  if ! id -u $kUID; then
      echo "Adding group $kUID (user $USER)"
      groupadd -g $kUID $USER
  fi
  echo "Checking if user already exists $kUID ..."
  if ! id $kUID; then
      echo "Adding user $kUID (user $USER)"
      useradd -u $kUID -g $kUID -m $USER
  fi
  echo "Setting samba password for ${USER}"
  ( echo ${PASSWORD} ; echo ${PASSWORD}; ) | smbpasswd -a "${USER}"

  mkdir -vp /smb/output/$USER || true
  chmod 777 /smb/output/$USER || true
  echo "OK `date`" > /smb/output/$USER/ok.txt || true
  chmod 777 /smb/output/$USER/ok.txt || true
}

function delete_user() {
	USER=$1
	echo "Deleting user $USER"
	smbpasswd -x "$USER"
	sleep 5
	userdel -r "$USER"
}

set -e

USERNAME=nautahealthcheck
USERID=1499
PASSWORD=`python3.6 -c "
import string
import random
print(''.join(random.choice(string.ascii_letters + string.digits) for i in range(20)))
"`

set +e

delete_user "$USERNAME"

set -e

create_user $USERNAME $USERID $PASSWORD

python3.6 -c '
import tempfile
import sys
from smb.SMBConnection import SMBConnection
conn = SMBConnection(sys.argv[1], sys.argv[2], "localhost", "localhost", use_ntlm_v2 = True)
assert conn.connect("localhost", 139)
file_obj = tempfile.NamedTemporaryFile()
file_attributes, filesize = conn.retrieveFile(sys.argv[3], sys.argv[4], file_obj)
file_obj.seek(0)
text = file_obj.read().decode("utf-8")
print("healthcheck file content: ", text)
if "OK" not in text:
    print("invalid contents of healthcheck file!")
    sys.exit(1)
file_obj.close()
sys.exit(0)
' "$USERNAME" "$PASSWORD" "output" "/ok.txt"
SMBCONNECT_RC=$?


delete_user "$USERNAME"

