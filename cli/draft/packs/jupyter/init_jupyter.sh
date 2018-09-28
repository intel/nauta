#!/usr/bin/env bash
shopt -s extglob
set +H

mkdir -p /mnt/output/home/${EXP_NAME}
mkdir -p /mnt/output/experiment/${EXP_NAME}

mv -t /mnt/output/experiment/${EXP_NAME} !(input|output)

jupyter notebook --allow-root
