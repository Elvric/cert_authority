#!/bin/sh
apt-get install nginx -y
cp /webserver/nginx/nginx.conf /etc/nginx/sites-available/default
mkdir /etc/nginx/ssl
cp -r /webserver/frontend/build/* /var/www/html/
cp /webserver/cert/* /etc/nginx/ssl