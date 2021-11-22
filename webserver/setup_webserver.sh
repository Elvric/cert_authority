#!/bin/sh
apt-get install net-tools nginx -y
cp webserver/nginx/nginx.conf /etc/nginx/sites-available/default
mkdir -p /etc/nginx/ssl
cp webserver/cert/* /etc/nginx/ssl
cp -r webserver/frontend/build/* /var/www/html/
sudo systemctl restart nginx