#!/usr/bin/env bash
#scli wrapper

set -e

scli --accept_license --mdm_ip "$SCLI_MDM" --login --username $SCLI_USERNAME --password $SCLI_PASSWORD
scli --mdm_ip "$SCLI_MDM" $@
