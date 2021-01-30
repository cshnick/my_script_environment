#!/bin/bash

COUNTRY="BY"
ST="Minsk"
L="Minsk"
O="Stub"
OU="Stub Department"
CN="cshnick.info"


echo "Generating ssl key and cert for"
echo "COUNTRY=$COUNTRY"
echo "ST=$ST"
echo "L=$L"
echo "O=$O"
echo "OU=$OU"
echo "CN=$CN"
openssl req -newkey rsa:4096 \
            -x509 \
            -sha256 \
            -days 3650 \
            -nodes \
            -out "$CN.crt" \
            -keyout "$CN.key" \
            -subj "/C=${COUNTRY}/ST=${ST}/L=${L}/O=${O}/OU=${OU}/CN=${CN}"
echo "Generation finished"
echo "$CN.key and $CN.crt generated"
