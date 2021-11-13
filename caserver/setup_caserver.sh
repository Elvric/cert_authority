#!/bin/sh
apt update
apt install nginx python3 python3-pip -y
pip3 install uwsgi
cp /tmp/setup/nginx/nginx.conf /etc/nginx/sites-available/default
mkdir /etc/nginx/ssl
cp /tmp/setup/cert/* /etc/nginx/ssl