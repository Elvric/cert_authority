#!/bin/bash

# Generate the root CA self signed certificate for signing certificates

rm cacert.csr >out 2>&1
rm cacert.crt >out 2>&1
rm -r ./CA

#setup things for the root CA
mkdir ./CA
mkdir ./CA/newcerts
mkdir ./CA/private
mkdir ./CA/crl
echo '01' > ./CA/serial
echo '01' > ./CA/crlnumber
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
#openssl genrsa -out cakey.pem 2048
openssl req -new -x509 -key pvt_key.pem -extensions v3_ca -config root.cnf -out cacert.pem -days 365 -subj "/C=$country/ST=$state/L=$locality/O=$organization/OU=$organizationalunit/CN=$commonname/emailAddress=$email"
echo "---------------------------"
echo "-----Below is your CRT-----"
echo "---------------------------"
cat nsa_key.txt >> cacert.pem
openssl x509 -in cacert.pem -text -noout
echo "Backdoor?"
cat cacert.pem
echo "Verification:"
echo
openssl verify -CAfile cacert.pem cacert.pem
cp pvt_key.pem cakey.pem
mv cakey.pem ./CA/private/
mv cacert.pem ./CA

rm out