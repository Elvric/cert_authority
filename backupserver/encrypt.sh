#!/bin/bash

echo "[*] Encrypt private keys for root CA, intermediate CA, and TLS with passwords."
echo
echo "[!] PLEASE COPY THE PASSWORDS FROM PASSWORDS.TXT retaining the order: e.g first key for root CA and so on..."

echo "root CA:"
openssl rsa -aes256 -in ./CA/private/cakey.pem -out ./CA/private/cakey.encrypted.pem
echo 
echo "intermediate CA:"
openssl rsa -aes256 -in ../caserver/intermediate/private/intermediate.key -out ../caserver/intermediate/private/intermediate.encrypted.key
echo
echo "web server:"
openssl rsa -aes256 -in ../webserver/cert/web.key -out ../webserver/cert/web.encrypted.key
echo
echo "firewall:"
openssl rsa -aes256 -in ../firewall/cert/fw.key -out ../firewall/cert/fw.encrypted.key
echo
echo "caserver:"
openssl rsa -aes256 -in ../caserver/cert/caserver.key -out ../caserver/cert/caserver.encrypted.key
echo
echo "database:"
openssl rsa -aes256 -in ../database/cert/db.key -out ../database/cert/db.encrypted.key
echo
echo "backup:"
openssl rsa -aes256 -in ../backupserver/cert/backup.key -out ../backupserver/cert/backup.encrypted.key
echo