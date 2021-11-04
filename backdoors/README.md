Just run `klepto_v2.py`. It will generate:
- `pub_key.pem` being the public key with the backdoor
- `pvt_key.pem` being the private key.

For generating the self-signed certificate, just run `generate_self_signed_cert.sh`.
It will create a self signed certificate for the root CA of IMovies for which it can sign certificates for the machines using TLS and the users.
The private key and certificate for the root CA will be copied to `backupserver/CA/private` and `backupserver/CA/`  