#!/bin/sh
apt update
apt install nginx -y
cp nginx/nginx.conf /etc/nginx/sites-available/default
mkdir /etc/nginx/ssl
cp cert/* /etc/nginx/ssl
apt install python3 python3-pip -y
pip3 install uwsgi

pip3 install -r /caserver/api/requirements.txt 
service nginx restart
uwsgi --ini /caserver/api/uwsgi.ini 