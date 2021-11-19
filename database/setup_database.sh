#!/bin/bash
echo -n 'CREATE DATABASE imovies;' | sudo mysql -u root -pFiE5HF4xHOsPIL9n

export MYSQL_ROOT_PASSWORD=FiE5HF4xHOsPIL9n

mkdir /tmp/setup
cp imovies_users.sql /tmp/setup/
cp initdatabase.sql /tmp/setup/
cp my.cnf /etc/mysql/conf.d
cp cert/cacert.pem /etc/mysql/ssl/cacert.pem
cp cert/db.pem /etc/mysql/ssl/db-cert.pem
cp cert/db.key /etc/mysql/ssl/db-key.pem

chown mysql /etc/mysql/ssl/db-cert.pem
chown mysql /etc/mysql/ssl/db-key.pem
chmod 644 /etc/mysql/ssl/cacert.pem
chmod 644 /etc/mysql/ssl/db-cert.pem
chmod 600 /etc/mysql/ssl/db-key.pem

sudo mysql -u root -pFiE5HF4xHOsPIL9n imovies < /tmp/setup/imovies_users.sql
sudo mysql -u root -pFiE5HF4xHOsPIL9n imovies < /tmp/setup/initdatabase.sql