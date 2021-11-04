# Setup
Before starting, make sure that you have in this dir:
- pub_key.pem
- pvt_key.pem
- nsa_key.txt
If you don't, go to `backdoors` and run `./backdoor.sh`.
Also make sure that you have the config file for openssl `root.cnf`.

# Create the self signed root CA certificate
Run `./generate_self_signed_cert.sh`. It will generate the `./CA` directory containing the private key of the rootCA (in `/CA/private`), the certificate `cacert.pem` and all the necessary directories.

# Sign the certificates for the services
Once you have set up the root CA, run `./sign_certificates`. It will store the certificates on the other directories in the `/<service name>/cert` directory. You will also find the certificates in the `./CA/newcerts` directory and in the `./CA/machine_certs/<service name>` with also the private key of the service and the signing request.