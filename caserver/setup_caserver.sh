#!/bin/sh
cp ./caserver/cert/cacert.pem /etc/ssl/certs/
sudo apt update
sudo apt install nginx net-tools rsyslog-gnutls -y
sudo apt install libpcre3 libpcre3-dev -y
sudo cp caserver/nginx/nginx.conf /etc/nginx/sites-available/default
cp caserver/log/* /etc/rsyslog.d/
sudo mkdir -p /etc/nginx/ssl
sudo cp caserver/cert/* /etc/nginx/ssl
sudo cp caserver/intermediate/intermediate.pem /etc/nginx/ssl/intermediate.pem
sudo cp caserver/intermediate/ca-chain.pem /etc/nginx/ssl/ca-chain.pem
sudo cp caserver/intermediate/private/intermediate.key /etc/nginx/ssl/intermediate.key
sudo chown www-data:www-data /etc/nginx/ssl/intermediate.pem /etc/nginx/ssl/intermediate.key
sudo apt install python3 python3-pip -y
cd caserver/api
pip3 install -r requirements.txt
sudo systemctl link /home/vagrant/caserver/api/caserver.service
sudo systemctl enable caserver.service
sudo systemctl start caserver.service
sudo systemctl restart caserver.service
sudo systemctl restart nginx
systemctl restart rsyslog

# Rsyslog
cp caserver/rsyslog.conf /etc/rsyslog.conf
systemctl restart rsyslog