#!/bin/bash -e

/sbin/iptables -t nat -F REDSOCKS || exit 0
/sbin/iptables -t nat -S | grep '\-j REDSOCKS' | cut -d ' ' -f 2- | while read -r LINE; do /sbin/iptables -t nat -D $LINE; done
/sbin/iptables -t nat -X REDSOCKS
