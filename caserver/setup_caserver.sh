#!/bin/sh
sudo apt update
sudo apt install nginx net-tools -y
sudo apt install libpcre3 libpcre3-dev -y
sudo cp caserver/nginx/nginx.conf /etc/nginx/sites-available/default
sudo mkdir /etc/nginx/ssl
sudo cp caserver/cert/* /etc/nginx/ssl
sudo sudo cp caserver/intermediate/intermediate.pem /etc/nginx/ssl/intermediate.pem
sudo apt install python3 python3-pip -y
cd caserver/api
pip3 install -r requirements.txt
sudo systemctl restart nginx