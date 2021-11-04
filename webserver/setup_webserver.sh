#!/bin/sh
echo "SETUP IN PROGRESS"
apt-get install nginx -y
cp /tmp/setup/nginx/webserver /etc/nginx/sites-available/default

service nginx restart