#!/bin/bash
echo -n 'CREATE DATABASE imovies;' | mysql -u root -pFiE5HF4xHOsPIL9n
mysql -u root -pFiE5HF4xHOsPIL9n imovies < /tmp/setup/imovies_users.sql
mysql -u root -pFiE5HF4xHOsPIL9n imovies < /tmp/setup/initdatabase.sql