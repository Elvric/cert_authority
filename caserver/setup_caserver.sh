#!/bin/sh
apt update
apt install nginx python3 -y
cp /tmp/setup/nginx/nginx.conf /etc/nginx/sites-available/default
mkdir /etc/nginx/ssl
cp /tmp/setup/cert/* /etc/nginx/ssl