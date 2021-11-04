#!/bin/bash

../../backdoors/generate_self_signed_cert.sh

commonname_web=web.imovies.ch. #maybe remove . at the end
commonname_fw=firewall.imovies.ch.
commonname_caserver=server.imovies.ch.
commonname_db=db.imovies.ch.
commonname_backup=backup.imovies.ch
#Change to your company details
country=CH
state=VD
locality=Lausanne
organization=IMovies
organizationalunit_web=Web
organizationalunit_fw=Firewall
organizationalunit_caserver=Server
organizationalunit_db=DB
organizationalunit_backuo=Backup
email=admin@imovies.ch

echo "Creating certificate for Web"
openssl req -new -newkey rsa:1024 -nodes -keyout web.key -out web.csr -subj "/C=$country/ST=$state/L=$locality/O=$organization/OU=$organizationalunit_web/CN=$commonname_web/emailAddress=$email"

openssl x509 -req -sha256 -days 365 -in web.csr -signkey ./CA/private/cakey.pem -out web.crt
echo "Done!"

echo "Creating certificate for Web"
openssl req -new -newkey rsa:1024 -nodes -keyout web.key -out web.csr -subj "/C=$country/ST=$state/L=$locality/O=$organization/OU=$organizationalunit_fw/CN=$commonname_fw/emailAddress=$email"

openssl x509 -req -sha256 -days 365 -in web.csr -signkey ./CA/private/cakey.pem -out web.crt
echo "Done!"

echo "Creating certificate for Web"
openssl req -new -newkey rsa:1024 -nodes -keyout web.key -out web.csr -subj "/C=$country/ST=$state/L=$locality/O=$organization/OU=$organizationalunit/CN=$commonname/emailAddress=$email"

openssl x509 -req -sha256 -days 365 -in web.csr -signkey ./CA/private/cakey.pem -out web.crt
echo "Done!"

echo "Creating certificate for Web"
openssl req -new -newkey rsa:1024 -nodes -keyout web.key -out web.csr -subj "/C=$country/ST=$state/L=$locality/O=$organization/OU=$organizationalunit/CN=$commonname/emailAddress=$email"

openssl x509 -req -sha256 -days 365 -in web.csr -signkey ./CA/private/cakey.pem -out web.crt
echo "Done!"

echo "Creating certificate for Web"
openssl req -new -newkey rsa:1024 -nodes -keyout web.key -out web.csr -subj "/C=$country/ST=$state/L=$locality/O=$organization/OU=$organizationalunit/CN=$commonname/emailAddress=$email"

openssl x509 -req -sha256 -days 365 -in web.csr -signkey ./CA/private/cakey.pem -out web.crt
echo "Done!"
