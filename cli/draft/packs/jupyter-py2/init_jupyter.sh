#!/usr/bin/env bash
shopt -s extglob
set +H

mkdir -p /mnt/output/home/${EXP_NAME}

mv -t /mnt/output/experiment !(input|output)

jupyter notebook --allow-root
