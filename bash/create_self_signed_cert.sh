#!/bin/bash

DOMAIN=localhost
if [[ -n $1 ]] ; then
  DOMAIN=$1
fi

CA_NAME=cshnickCA
COUNTRY="BY"
ST="Minsk"
L="Minsk"
O="cshnick"
OU="cshnick home"
CN="$DOMAIN"

function get_current_ipv4() {
  local ip4=$(/sbin/ip -o -4 addr list eth0 | awk '{print $4}' | cut -d/ -f1)
  echo $ip4
}

function install_self_signed_v1() {
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
}

function install_self_signed_v2() {
  echo "Become a Certificate Authority"

  echo "Generate private key"
  openssl genrsa -out $CA_NAME.key 4096
  echo "Generate root certificate"
  openssl req -x509 -new -nodes -key $CA_NAME.key -sha256 -days 3650 -out $CA_NAME.pem

  echo "Create CA-signed certs"

  NAME=$DOMAIN # Use your own domain name
  echo "Generate a private key"
  openssl genrsa -out $NAME.key 4096
  echo "Create a certificate-signing request"
  openssl req -new -key $NAME.key -out $NAME.csr
  echo "Create a config file for the extensions"
  >$NAME.ext cat <<-EOF
authorityKeyIdentifier=keyid,issuer
basicConstraints=CA:FALSE
keyUsage = digitalSignature, nonRepudiation, keyEncipherment, dataEncipherment
subjectAltName = @alt_names
[alt_names]
DNS.1 = $NAME # Be sure to include the domain name here because Common Name is not so commonly honoured by itself
DNS.2 = test.$NAME # Optionally, add additional domains (I've added a subdomain here)
IP.1 = $(get_current_ipv4) # Optionally, add an IP address (if the connection which you have planned requires it)
EOF
  # Create the signed certificate
  openssl x509 -req -in $NAME.csr -CA $CA_NAME.pem -CAkey $CA_NAME.key -CAcreateserial \
  -out $NAME.crt -days 825 -sha256 -extfile $NAME.ext
}

install_self_signed_v2
