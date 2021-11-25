#!/bin/sh
cp ./caserver/cert/cacert.pem /etc/ssl/certs/
sudo apt update
sudo apt install nginx net-tools rsyslog-gnutls -y
sudo apt install libpcre3 libpcre3-dev -y
sudo cp caserver/nginx/nginx.conf /etc/nginx/sites-available/default
sudo mkdir -p /etc/nginx/ssl
sudo mkdir -p /etc/ca/intermediate
sudo cp caserver/cert/* /etc/nginx/ssl
sudo cp caserver/intermediate/intermediate.pem /etc/nginx/ssl/intermediate.pem
sudo cp caserver/intermediate/ca-chain.pem /etc/nginx/ssl/ca-chain.pem
sudo cp caserver/intermediate/private/intermediate.key /etc/nginx/ssl/intermediate.key
sudo cp -r caserver/api/intermediate/ /etc/ca/
sudo cp caserver/api/intermediate/intermediate.pem /etc/nginx/ssl/intermediate.pem
sudo cp caserver/api/intermediate/ca-chain.pem /etc/nginx/ssl/ca-chain.pem
sudo cp caserver/api/intermediate/private/intermediate.key /etc/nginx/ssl/intermediate.key
#sudo chown www-data:www-data /etc/nginx/ssl/cacert.pem /etc/nginx/ssl/cakey.pem
#sudo cp caserver/intermediate /etc/ca/intermediate
sudo chown www-data:www-data /etc/nginx/ssl/intermediate.pem /etc/nginx/ssl/intermediate.key
sudo chown www-data:www-data /etc/ca /etc/ca/intermediate
sudo chown www-data:www-data /etc/ca/intermediate/*
sudo chown www-data:www-data /etc/ca/intermediate/private/intermediate.key
sudo chown www-data:www-data /etc/ca/intermediate/certificates
sudo chown www-data:www-data /etc/ca/intermediate/private
sudo chown www-data:www-data /etc/ca/intermediate/crl
sudo chown www-data:www-data /etc/ca/intermediate/newcerts
sudo chmod +x /etc/ca/intermediate/new_cert.sh
sudo mkdir -p /var/log/flask
sudo chown www-data:www-data /var/log/flask
#sudo chown www-data:www-data /etc/ca/intermediate
#sudo chown www-data:www-data /etc/ca/intermediate/private/intermediate.key
sudo apt install python3 python3-pip -y
cd caserver/api
pip3 install -r requirements.txt
sudo systemctl link /home/vagrant/caserver/api/caserver.service
sudo systemctl enable caserver.service
sudo systemctl start caserver.service
sudo systemctl restart caserver.service
sudo systemctl restart nginx

# Rsyslog
cp caserver/rsyslog.conf /etc/rsyslog.conf
systemctl restart rsyslog