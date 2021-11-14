#!/bin/sh
apt update
apt install nginx -y
cp /tmp/setup/nginx/nginx.conf /etc/nginx/sites-available/default
mkdir /etc/nginx/ssl
cp /tmp/setup/cert/* /etc/nginx/ssl
apt install python3 python3-pip -y
pip3 install uwsgi