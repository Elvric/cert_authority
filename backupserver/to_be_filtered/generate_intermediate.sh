#!/bin/bash

# Generate the intermediate certificate and pvt key used for client authentication

rm -r ../../caserver/intermediate > out 2>&1
mkdir ../../caserver/intermediate
mkdir ../../caserver/intermediate/newcerts
mkdir ../../caserver/intermediate/private
mkdir ../../caserver/intermediate/crl
touch ../../caserver/intermediate/index.txt
echo '01' > ../../caserver/intermediate/serial
echo '01' > ../../caserver/intermediate/crlnumber

commonname=caserver.imovies

#Change to your company details
country=CH
state=VD
locality=Lausanne
organization=IMovies
organizationalunit=Intermediate
email=admin@imovies.ch

#generate interm pvt key
openssl genrsa -out ../../caserver/intermediate/private/intermediate.key 2048
#cp pvt_key.pem ../../caserver/intermediate/private/intermediate.key
#create csr
openssl req -config intermediate.cnf -new -key ../../caserver/intermediate/private/intermediate.key -out intermediate.csr -subj "/C=$country/ST=$state/L=$locality/O=$organization/OU=$organizationalunit/CN=$commonname/emailAddress=$email"
#sign request with root CA
openssl ca -config root.cnf -extensions v3_intermediate_ca -days 365 -in intermediate.csr -out ../../caserver/intermediate/intermediate.pem
echo "Intermediate CA created:"
openssl x509 -noout -text -in ../../caserver/intermediate/intermediate.pem
echo "Creating certificate chain"
cat ../../caserver/intermediate/intermediate.pem ./CA/cacert.pem > ../../caserver/intermediate/ca-chain.pem

openssl verify -CAfile CA/cacert.pem ../../caserver/intermediate/intermediate.pem

rm out
rm intermediate.csr