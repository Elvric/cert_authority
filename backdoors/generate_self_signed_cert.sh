#!/bin/bash

rm cacert.csr >out 2>&1
rm cacert.crt >out 2>&1

commonname=imovies.ch. #maybe remove . at the end

#Change to your company details
country=CH
state=VD
locality=Lausanne
organization=IMovies
organizationalunit=CA
email=admin@imovies.ch

echo "Creating CSR..."
openssl req -new -key pvt_key.pem -out cacert.csr -subj "/C=$country/ST=$state/L=$locality/O=$organization/OU=$organizationalunit/CN=$commonname/emailAddress=$email"

openssl x509 -req -sha256 -days 365 -in cacert.csr -signkey pvt_key.pem -out cacert.crt
echo "Done!"
echo "Creating Certificate"
echo
echo "---------------------------"
echo "-----Below is your CRT-----"
echo "---------------------------"
openssl x509 -in cacert.crt -text -noout

#Move things to backupserver

rm -r ../backupserver/CA >out 2>&1
mkdir ../backupserver/CA
mkdir ../backupserver/CA/private
cat pvt_key.pem > cakey.pem
cp cakey.pem ../backupserver/CA/private/
cp cacert.crt ../backupserver/CA/
rm cakey.pem