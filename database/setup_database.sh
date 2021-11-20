#!/bin/bash
DBPASSWD=FiE5HF4xHOsPIL9n

debconf-set-selections <<< "mysql-server mysql-server/root_password password $DBPASSWD"
debconf-set-selections <<< "mysql-server mysql-server/root_password_again password $DBPASSWD"

sudo apt update
sudo apt install mysql-server net-tools -y

mysql -u root -p$DBPASSWD -e "CREATE DATABASE imovies"
mysql -u root -p$DBPASSWD imovies < imovies_users.sql
mysql -u root -p$DBPASSWD imovies < initdatabase.sql

cp my.cnf /etc/mysql/conf.d
mkdir /etc/mysql/ssl
cp ./cert/cacert.pem /etc/mysql/ssl/cacert.pem
cp ./cert/db.pem /etc/mysql/ssl/db-cert.pem
cp ./cert/db.key /etc/mysql/ssl/db-key.pem
sudo chown mysql /etc/mysql/ssl/db-cert.pem
sudo chown mysql /etc/mysql/ssl/db-key.pem
sudo chmod 644 /etc/mysql/ssl/cacert.pem
sudo chmod 644 /etc/mysql/ssl/db-cert.pem
sudo chmod 600 /etc/mysql/ssl/db-key.pem
sudo sed -i -e "s/127.0.0.1/172.27.0.3/g" /etc/mysql/mysql.conf.d/mysqld.cnf 
sudo systemctl restart mysql