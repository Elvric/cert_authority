#!/bin/sh
sudo apt update
sudo apt install net-tools -y
sudo sed -i -r "s/^#(net.ipv4.ip_forward=1)/\1/" /etc/sysctl.conf
sudo sysctl -p
sudo apt install -y iptables
sudo iptables -F
sudo iptables -P INPUT DROP
sudo iptables -P FORWARD DROP
sudo iptables -A INPUT -p tcp --dport 22 -j ACCEPT
sudo iptables -A OUTPUT -j ACCEPT
sudo iptables -A FORWARD -s 172.27.0.0/24 -j ACCEPT
sudo iptables -A FORWARD -p tcp --dport 22 -j ACCEPT
sudo iptables -A FORWARD -s 172.26.0.2 -p tcp --dport 443 -j ACCEPT
