#!/bin/bash

rm cacert.csr >out 2>&1
rm cacert.crt >out 2>&1
rm -r ./CA

#setup things for the root CA
mkdir ./CA
mkdir ./CA/newcerts
mkdir ./CA/private
echo '01' > ./CA/serial
touch ./CA/index.txt

commonname=imovies

#Change to your company details
country=CH
state=VD
locality=Lausanne
organization=IMovies
organizationalunit=CA
email=admin@imovies.ch

echo "Creating Certificate"
echo
openssl req -new -x509 -key pvt_key.pem -extensions v3_ca -config root.cnf -out cacert.pem -days 365 -subj "/C=$country/ST=$state/L=$locality/O=$organization/OU=$organizationalunit/CN=$commonname/emailAddress=$email"
echo "---------------------------"
echo "-----Below is your CRT-----"
echo "---------------------------"
openssl x509 -in cacert.pem -text -noout

echo "Verification:"
echo
openssl verify -CAfile cacert.pem cacert.pem

cp pvt_key.pem cakey.pem
mv cakey.pem ./CA/private
mv cacert.pem ./CA

rm out