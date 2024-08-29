#!/bin/bash
args=("$@")
openssl ecparam -name secp256k1 -genkey -noout -out ${args[0]}/private_key.pem
openssl ec -in etc/private_key.pem -pubout > ${args[0]}/public_key.pem
