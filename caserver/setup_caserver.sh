#!/bin/sh
sudo apt update
sudo apt install nginx net-tools -y
sudo apt install libpcre3 libpcre3-dev -y
sudo ip route add 172.26.0.0/24 via 172.27.0.254
sudo cp caserver/nginx/nginx.conf /etc/nginx/sites-available/default
sudo mkdir /etc/nginx/ssl
sudo cp caserver/cert/* /etc/nginx/ssl
sudo sudo cp caserver/intermediate/intermediate.pem /etc/nginx/ssl/intermediate.pem
sudo apt install python3 python3-pip -y
cd caserver/api
pip3 install -r requirements.txt
sudo systemctl restart nginx
sudo systemctl link /home/vagrant/caserver/api/caserver.service
sudo systemctl enable caserver.service
sudo systemctl start caserver.service