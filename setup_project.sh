#!/bin/bash
sudo apt update
sudo pip3 install virtualenv
mkdir -p ./caserver/api/venv
python3 -m virtualenv ./caserver/api/venv

sudo apt install nodejs
sudo apt install npm
cd webserver/frontend && npm install