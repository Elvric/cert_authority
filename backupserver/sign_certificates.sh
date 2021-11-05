#!/bin/bash

# Use the script to generate and sign the other certificates for tls

#store the other machine certs in root CA, just in case
rm -r ./CA/machine_certs >out 2>&1
mkdir ./CA/machine_certs
mkdir ./CA/machine_certs/web
mkdir ./CA/machine_certs/firewall
mkdir ./CA/machine_certs/caserver
mkdir ./CA/machine_certs/db
mkdir ./CA/machine_certs/backup

#we will store the tls certs in the cert directory on the other machines
rm -r ../webserver/cert >out 2>&1
rm -r ../firewall/cert >out 2>&1
rm -r ../caserver/cert >out 2>&1
rm -r ../database/cert >out 2>&1
rm -r ../backupserver/cert >out 2>&1

#define the machines common names, e.g web server will be https://web.imovies.ch
commonname_web=web.imovies
commonname_fw=firewall.imovies
commonname_caserver=server.imovies
commonname_db=db.imovies.
commonname_backup=backup.imovies

#fixed but the organizational unit to be more clear
country=CH
state=VD
locality=Lausanne
organization=IMovies
organizationalunit_web=Web
organizationalunit_fw=Firewall
organizationalunit_caserver=Server
organizationalunit_db=DB
organizationalunit_backup=Backup
email=admin@imovies.ch

echo "Creating certificate for Web"
openssl req -new -newkey rsa:1024 -nodes -keyout web.key -out web.csr -subj "/C=$country/ST=$state/L=$locality/O=$organization/OU=$organizationalunit_web/CN=$commonname_web/emailAddress=$email"

openssl ca -config root.cnf -in web.csr
echo "Done!"
echo
echo "Creating certificate for Firewall"
openssl req -new -newkey rsa:1024 -nodes -keyout fw.key -out fw.csr -subj "/C=$country/ST=$state/L=$locality/O=$organization/OU=$organizationalunit_fw/CN=$commonname_fw/emailAddress=$email"

openssl ca -config root.cnf -in fw.csr
echo "Done!"
echo
echo "Creating certificate for CA Server"
openssl req -new -newkey rsa:1024 -nodes -keyout caserver.key -out caserver.csr -subj "/C=$country/ST=$state/L=$locality/O=$organization/OU=$organizationalunit_caserver/CN=$commonname_caserver/emailAddress=$email"

openssl ca -config root.cnf -in caserver.csr
echo "Done!"
echo
echo "Creating certificate for DB"
openssl req -new -newkey rsa:1024 -nodes -keyout db.key -out db.csr -subj "/C=$country/ST=$state/L=$locality/O=$organization/OU=$organizationalunit_db/CN=$commonname_db/emailAddress=$email"

openssl ca -config root.cnf -in db.csr
echo "Done!"
echo
echo "Creating certificate for Backup"
openssl req -new -newkey rsa:1024 -nodes -keyout backup.key -out backup.csr -subj "/C=$country/ST=$state/L=$locality/O=$organization/OU=$organizationalunit_backup/CN=$commonname_backup/emailAddress=$email"

openssl ca -config root.cnf -in backup.csr
echo "Done!"
echo

#copy all the things in the directory in root CA
cp web.key ./CA/machine_certs/web
cp web.csr ./CA/machine_certs/web
cp ./CA/newcerts/01.pem web.pem
cp web.pem ./CA/machine_certs/web/web.pem

cp fw.key ./CA/machine_certs/firewall
cp fw.csr ./CA/machine_certs/firewall
cp ./CA/newcerts/02.pem fw.pem
cp fw.pem ./CA/machine_certs/firewall/firewall.pem

cp caserver.key ./CA/machine_certs/caserver
cp caserver.csr ./CA/machine_certs/caserver
cp ./CA/newcerts/03.pem caserver.pem
cp caserver.pem ./CA/machine_certs/caserver/caserver.pem

cp db.key ./CA/machine_certs/db
cp db.csr ./CA/machine_certs/db
cp ./CA/newcerts/04.pem db.pem
cp db.pem ./CA/machine_certs/db/db.pem

cp backup.key ./CA/machine_certs/backup
cp backup.csr ./CA/machine_certs/backup
cp ./CA/newcerts/05.pem backup.pem
cp backup.pem ./CA/machine_certs/backup/backup.pem


#dispatch the certificates and private keys to other machines
mkdir ../webserver/cert
mv web.key ../webserver/cert
rm web.csr
mv web.pem ../webserver/cert

mkdir ../firewall/cert
mv fw.key ../firewall/cert
rm fw.csr
mv fw.pem ../firewall/cert

mkdir ../caserver/cert
mv caserver.key ../caserver/cert
rm caserver.csr
mv caserver.pem ../caserver/cert

mkdir ../database/cert
mv db.key ../database/cert
rm db.csr
mv db.pem ../database/cert

mkdir ../backupserver/cert
mv backup.key ../backupserver/cert
rm backup.csr
mv backup.pem ../backupserver/cert

rm out
rm ./CA/index.txt.attr
rm ./CA/index.txt.attr.old
rm ./CA/index.txt.old
rm ./CA/serial.old