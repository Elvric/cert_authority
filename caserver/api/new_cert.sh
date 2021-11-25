#!/bin/bash
# use new_cert.sh <uid> <serial>
openssl genrsa -out ./certificates/client.key
openssl req -config intermediate.cnf -key ./certificates/client.key -new -sha256 -out ./certificates/client.csr -subj "/C=CH/ST=VD/L=Lausanne/O=IMovies/OU=CA/CN=client/emailAddress=admin@imovies.ch"
openssl ca -config intermediate.cnf -extensions usr_cert -days 365 -notext -md sha256 -in ./certificates/client.csr -out ./certificates/client.pem -batch
openssl pkcs12 -export -in ./certificates/client.pem -inkey ./certificates/client.key -out ./certificates/client$1_$2.p12 -password pass:pass