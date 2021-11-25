#!/bin/bash

# Generate the intermediate certificate and pvt key used for client authentication

rm -r ../../caserver/api/intermediate > out 2>&1
mkdir ../../caserver/api/intermediate
mkdir ../../caserver/api/intermediate/newcerts
mkdir ../../caserver/api/intermediate/private
mkdir ../../caserver/api/intermediate/crl
touch ../../caserver/api/intermediate/index.txt
echo '01' > ../../caserver/api/intermediate/serial
echo '01' > ../../caserver/api/intermediate/crlnumber

commonname=caserver.imovies

#Change to your company details
country=CH
state=VD
locality=Lausanne
organization=IMovies
organizationalunit=Intermediate
email=admin@imovies.ch

#generate interm pvt key
openssl genrsa -out ../../caserver/api/intermediate/private/intermediate.key 2048

#create csr
openssl req -config intermediate.cnf -new -key ../../caserver/api/intermediate/private/intermediate.key -out intermediate.csr -subj "/C=$country/ST=$state/L=$locality/O=$organization/OU=$organizationalunit/CN=$commonname/emailAddress=$email"
#sign request with root CA
openssl ca -config root.cnf -extensions v3_intermediate_ca -days 365 -in intermediate.csr -out ../../caserver/api/intermediate/intermediate.pem
echo "Intermediate CA created:"
openssl x509 -noout -text -in ../../caserver/api/intermediate/intermediate.pem
echo "Creating certificate chain"
cat ../../caserver/api/intermediate/intermediate.pem ./CA/cacert.pem > ../../caserver/api/intermediate/ca-chain.pem

openssl verify -CAfile CA/cacert.pem ../../caserver/api/intermediate/intermediate.pem

cp ../../caserver/api/intermediate/intermediate.pem ../../webserver/cert/
cp ../../caserver/api/intermediate/ca-chain.pem ../../webserver/cert/
rm out
rm intermediate.csr