#!/bin/bash
# use new_cert.sh <serial> <uid>
openssl genrsa -out /etc/ca/intermediate/certificates/client.key
openssl req -config /etc/ca/intermediate/intermediate.cnf -key /etc/ca/intermediate/certificates/client.key -new -sha256 -out /etc/ca/intermediate/certificates/client.csr -subj "/C=CH/ST=VD/L=Lausanne/O=IMovies/OU=CA/CN=$1_$2/emailAddress=admin@imovies.ch"
openssl ca -config /etc/ca/intermediate/intermediate.cnf -extensions usr_cert -days 365 -notext -md sha256 -in /etc/ca/intermediate/certificates/client.csr -out /etc/ca/intermediate/certificates/client.pem -batch
openssl pkcs12 -export -in /etc/ca/intermediate/certificates/client.pem -inkey /etc/ca/intermediate/certificates/client.key -out /etc/ca/intermediate/certificates/$1_$2.p12 -password pass:pass
rm /etc/ca/intermediate/certificates/client.key
rm /etc/ca/intermediate/certificates/client.pem