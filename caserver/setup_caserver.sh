#!/bin/sh
apt update
apt install nginx net-tools rsyslog-gnutls -y
apt install libpcre3 libpcre3-dev -y
cp caserver/nginx/nginx.conf /etc/nginx/sites-available/default
mkdir -p /etc/nginx/ssl
mkdir -p /etc/ca/intermediate
cp caserver/cert/* /etc/nginx/ssl
cp caserver/intermediate/ca-chain.pem /etc/nginx/ssl/ca-chain.pem
cp caserver/intermediate/private/intermediate.key /etc/nginx/ssl/intermediate.key
cp -r caserver/api/intermediate/ /etc/ca/
cp caserver/api/intermediate/intermediate.pem /etc/nginx/ssl/intermediate.pem
cp caserver/api/intermediate/ca-chain.pem /etc/nginx/ssl/ca-chain.pem
cp caserver/api/intermediate/private/intermediate.key /etc/nginx/ssl/intermediate.key
chown www-data:www-data /etc/nginx/ssl/intermediate.pem /etc/nginx/ssl/intermediate.key
chown www-data:www-data /etc/ca /etc/ca/intermediate
chown www-data:www-data /etc/ca/intermediate/*
chown www-data:www-data /etc/ca/intermediate/private/intermediate.key
chown www-data:www-data /etc/ca/intermediate/certificates
chown www-data:www-data /etc/ca/intermediate/private
chown www-data:www-data /etc/ca/intermediate/crl
chmod +x /etc/ca/intermediate/new_cert.sh
mkdir -p /var/log/flask
chown www-data:www-data /var/log/flask
apt install python3 python3-pip -y
cd caserver/api
pip3 install -r requirements.txt
systemctl link /home/vagrant/caserver/api/caserver.service
systemctl enable caserver.service
systemctl start caserver.service
systemctl restart caserver.service
systemctl restart nginx

# Rsyslog
cd "/home/vagrant"
cp ./caserver/cert/cacert.pem /etc/ssl/certs/
cp ./caserver/log/rsyslog.conf /etc/rsyslog.conf
cp caserver/log/nginx.conf /etc/rsyslog.d/nginx.log
systemctl restart rsyslog