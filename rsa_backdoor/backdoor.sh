#!/bin/bash

python3 klepto_v2.py
mv pvt_key.pem ../backupserver
mv pub_key.pem ../backupserver
mv nsa_key.txt ../backupserver

rm out