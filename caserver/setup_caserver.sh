#!/bin/sh
apt update
apt install nginx net-tools rsyslog-gnutls -y
apt install libpcre3 libpcre3-dev -y
cp caserver/nginx/nginx.conf /etc/nginx/sites-available/default
mkdir -p /etc/nginx/ssl
mkdir -p /etc/ca/intermediate
cp caserver/cert/* /etc/nginx/ssl
cp -R caserver/api/intermediate/* /etc/ca/intermediate
chown -R www-data:www-data /etc/ca
chmod u+x /etc/ca/intermediate/new_cert.sh
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