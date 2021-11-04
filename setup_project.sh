#!/bin/bash
sudo apt update
sudo apt install pipenv
sudo pip3 install virtualenv
mkdir ./caserver/venv
virtualenv ./caserver/venv

sudo apt install nodejs
sudo apt install npm
cd webserver/frontend && npm install