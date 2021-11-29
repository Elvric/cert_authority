#!/bin/sh
apt-get install net-tools nginx -y
cp webserver/nginx/nginx.conf /etc/nginx/sites-available/default
mkdir -p /etc/nginx/ssl
cp webserver/cert/* /etc/nginx/ssl
cp -r webserver/frontend/build/* /var/www/html/
cat <<EOF > /etc/hosts
172.27.0.2 caserver.imovies
127.0.0.1       localhost
127.0.1.1       ubuntu2004.localdomain

# The following lines are desirable for IPv6 capable hosts
::1     localhost ip6-localhost ip6-loopback
ff02::1 ip6-allnodes
ff02::2 ip6-allrouters

127.0.0.1 ubuntu2004.localdomain
EOF
systemctl restart nginx

# firewall
sudo apt install -y iptables
sudo iptables -F
sudo iptables -P INPUT DROP
sudo iptables -P FORWARD DROP
sudo iptables -A FORWARD -s 172.26.0.0/24 -j ACCEPT
sudo iptables -A FORWARD -p tcp --dport 22 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 22 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 443 -j ACCEPT
sudo iptables -A INPUT -p icmp --icmp-type echo-request -j DROP
sudo iptables -A INPUT -s 172.27.0.2 -j ACCEPT

# rsyslog
apt install rsyslog-gnutls -y
cp webserver/log/rsyslog.conf /etc/rsyslog.conf
cp webserver/log/nginx.conf /etc/rsyslog.d/nginx.conf
systemctl restart rsyslog
