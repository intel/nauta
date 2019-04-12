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

for FOLDER in /data/gitea/conf /data/gitea/log /data/git /data/ssh; do
    mkdir -p ${FOLDER}
done

############# SSH SETUP ###################

if [ ! -d /data/ssh ]; then
    mkdir -p /data/ssh
fi

if [ ! -f /data/ssh/ssh_host_ed25519_key ]; then
    echo "Generating /data/ssh/ssh_host_ed25519_key..."
    ssh-keygen -t ed25519 -f /data/ssh/ssh_host_ed25519_key -N "" > /dev/null
fi

if [ ! -f /data/ssh/ssh_host_rsa_key ]; then
    echo "Generating /data/ssh/ssh_host_rsa_key..."
    ssh-keygen -t rsa -b 2048 -f /data/ssh/ssh_host_rsa_key -N "" > /dev/null
fi

if [ ! -f /data/ssh/ssh_host_dsa_key ]; then
    echo "Generating /data/ssh/ssh_host_dsa_key..."
    ssh-keygen -t dsa -f /data/ssh/ssh_host_dsa_key -N "" > /dev/null
fi

if [ ! -f /data/ssh/ssh_host_ecdsa_key ]; then
    echo "Generating /data/ssh/ssh_host_ecdsa_key..."
    ssh-keygen -t ecdsa -b 256 -f /data/ssh/ssh_host_ecdsa_key -N "" > /dev/null
fi

chown root:root /data/ssh/*
chmod 0700 /data/ssh
chmod 0600 /data/ssh/*

############### GITEA SETUP ##########################

if [ ! -d /data/git/.ssh ]; then
    mkdir -p /data/git/.ssh
    chmod 700 /data/git/.ssh
fi

if [ ! -f /data/git/.ssh/environment ]; then
    echo "GITEA_CUSTOM=/data/gitea" >| /data/git/.ssh/environment
    chmod 600 /data/git/.ssh/environmentauthorized_keys
fi

if [ ! -f /data/gitea/conf/app.ini ]; then
    mkdir -p /data/gitea/conf

    # Set INSTALL_LOCK to true only if SECRET_KEY is not empty and
    # INSTALL_LOCK is empty
    if [ -n "$SECRET_KEY" ] && [ -z "$INSTALL_LOCK" ]; then
        INSTALL_LOCK=true
    fi

    # Substitude the environment variables in the template
    APP_NAME=${APP_NAME:-"Gitea: Git with a cup of tea"} \
    RUN_MODE=${RUN_MODE:-"dev"} \
    SSH_DOMAIN=${SSH_DOMAIN:-"localhost"} \
    HTTP_PORT=${HTTP_PORT:-"3000"} \
    ROOT_URL=${ROOT_URL:-""} \
    DISABLE_SSH=${DISABLE_SSH:-"false"} \
    SSH_PORT=${SSH_PORT:-"22"} \
    DB_TYPE=${DB_TYPE:-"sqlite3"} \
    DB_HOST=${DB_HOST:-"localhost:3306"} \
    DB_NAME=${DB_NAME:-"gitea"} \
    DB_USER=${DB_USER:-"root"} \
    DB_PASSWD=${DB_PASSWD:-""} \
    INSTALL_LOCK=${INSTALL_LOCK:-"false"} \
    DISABLE_REGISTRATION=${DISABLE_REGISTRATION:-"false"} \
    REQUIRE_SIGNIN_VIEW=${REQUIRE_SIGNIN_VIEW:-"false"} \
    SECRET_KEY=${SECRET_KEY:-""} \
    envsubst < /etc/templates/app.ini > /data/gitea/conf/app.ini
fi

# only chown if current owner is not already the gitea ${USER}. No recursive check to save time
if ! [[ $(ls -ld /data/gitea | awk '{print $3}') = ${USER} ]]; then chown -R ${USER}:git /data/gitea; fi
if ! [[ $(ls -ld /app/gitea  | awk '{print $3}') = ${USER} ]]; then chown -R ${USER}:git /app/gitea;  fi
if ! [[ $(ls -ld /data/git   | awk '{print $3}') = ${USER} ]]; then chown -R ${USER}:git /data/git;   fi
chmod 0755 /data/gitea /app/gitea /data/git

################ START THEM #################################

/usr/sbin/sshd -D &

runuser -u git /app/gitea/gitea web

sleep 30
