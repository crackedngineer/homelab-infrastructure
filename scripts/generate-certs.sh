#!/bin/bash

CERT_DIR="./certs"
DOMAIN="homelab"

mkdir -p $CERT_DIR

echo "🔐 Installing local CA..."
mkcert -install

echo "📜 Generating wildcard cert..."
mkcert -cert-file $CERT_DIR/_.$DOMAIN.pem \
       -key-file $CERT_DIR/_.$DOMAIN-key.pem \
       "*.$DOMAIN"

echo "✅ Certificates generated in $CERT_DIR"