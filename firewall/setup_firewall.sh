#!/bin/sh
# TODO to be uncommented in final version
#sudo apt update
#sudo apt install -y iptables
#sudo iptables -P INPUT DROP
#sudo iptables -P FORWARD DROP
#sudo iptables -P OUTPUT DROP
#sudo iptables -A FORWARD -s 172.27.0.0/16 -j ACCEPT
#sudo iptables -A FORWARD -p tcp --dport 22 -j ACCEPT
#sudo iptables -A FORWARD -s 172.26.0.2 -p tcp -dport 443 -j ACCEPT