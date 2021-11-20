#!/bin/bash

./generate_self_signed_cert.sh
./sign_certificates.sh
./generate_intermediate.sh