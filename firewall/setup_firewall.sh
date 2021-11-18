#!/bin/sh
apt update
apt install -y iptables
iptables -F
iptables -P INPUT DROP
iptables -P FORWARD DROP
iptables -P OUTPUT DROP
iptables -A FORWARD -s 172.27.0.0/16 -j ACCEPT
iptables -A FORWARD -p tcp --dport 22 -j ACCEPT
iptables -A FORWARD -s 172.26.0.2 -p tcp --dport 443 -j ACCEPT