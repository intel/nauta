#!/bin/bash

IP=$(dig +short host.docker.internal)

/usr/bin/socat TCP-LISTEN:$1,fork,reuseaddr TCP:$IP:$1

