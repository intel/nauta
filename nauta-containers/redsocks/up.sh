#!/bin/bash -e
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


# Cleanup
/down.sh

# Enable net ipv4 forwarding
/bin/sh -c "echo 1 > /proc/sys/net/ipv4/ip_forward"
/bin/sh -c "echo 1 > /proc/sys/net/ipv4/tcp_syncookies"
/bin/sh -c "echo 1 > /proc/sys/net/ipv4/conf/all/rp_filter"
/bin/sh -c "echo 1 > /proc/sys/net/ipv4/icmp_echo_ignore_broadcasts"
/bin/sh -c "echo 1 > /proc/sys/net/ipv4/icmp_ignore_bogus_error_responses"

/sbin/iptables -t nat -N REDSOCKS

# Ignore all traffic to private networks
/sbin/iptables -t nat -A REDSOCKS -d 0.0.0.0/8 -j RETURN
/sbin/iptables -t nat -A REDSOCKS -d 10.0.0.0/8 -j RETURN
/sbin/iptables -t nat -A REDSOCKS -d 127.0.0.0/8 -j RETURN
/sbin/iptables -t nat -A REDSOCKS -d 192.168.0.0/16 -j RETURN
/sbin/iptables -t nat -A REDSOCKS -d 224.0.0.0/4 -j RETURN
/sbin/iptables -t nat -A REDSOCKS -d 240.0.0.0/4 -j RETURN

# Ignore custom networks
echo ${IGNORED_NETWORKS:-} | sed 's/,/ /g' | while read -r IP; do /sbin/iptables -t nat -A REDSOCKS -d $IP -j RETURN; done

# Redirect all tcp traffic to REDSOCKS port
/sbin/iptables -t nat -A REDSOCKS -p tcp -j DNAT --to-destination ${IP}:${PORT}

# Render configuration
eval "/bin/cat <<< \"$(</redsocks.conf)\"" > /etc/redsocks.conf
cat /etc/redsocks.conf
/usr/sbin/redsocks -t -c /etc/redsocks.conf -p /tmp/redsocks.pid
/usr/sbin/redsocks -c /etc/redsocks.conf -p /tmp/redsocks.pid

# Redirect all traffic from local networks to redsocks
echo ${INTERFACES:-} | sed 's/,/ /g' | while read -r INTERFACE; do /sbin/iptables -t nat -A PREROUTING -i $INTERFACE -p tcp -j REDSOCKS; done

PID=$(cat /tmp/redsocks.pid)
while kill -0 $PID; do
    sleep 1
done

# Cleanup
/down.sh
