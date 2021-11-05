# Setup
Before starting, make sure that you have in this dir:
- pub_key.pem (this is not really used...)
- pvt_key.pem
- nsa_key.txt

If you don't, go to `backdoors` and run `./backdoor.sh`.

Also make sure that you have the config file for openssl `root.cnf` and `intermediate.cnf` in this directory.

# Run
Run `./certs.sh`. It will handle everything for you. It will generate the root CA, make it sign the certificates
for TLS connection between machines and also create the Intermediate CA for Client Authentication.

You can find the root CA in `backupserver/CA/`

You can then find the certificates and private keys in `<service>/cert` and the intermediate CA in `caserver/intermediate/`

# Encrypt private keys
Run `./encrypt.sh` to generate the encrypted versions of the private keys. You will find the passphrases in passwords.txt.

Please use them in order, e.g first for root CA and so on