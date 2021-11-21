#!/bin/sh
apt-get install net-tools nginx -y
sudo ip route add 172.26.0.0/24 via 172.27.0.254
cp webserver/nginx/nginx.conf /etc/nginx/sites-available/default
mkdir /etc/nginx/ssl
cp -r webserver/frontend/build/* /var/www/html/
cp webserver/cert/* /etc/nginx/ssl