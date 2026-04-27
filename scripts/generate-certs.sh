#!/bin/bash

CERT_DIR="/etc/traefik/certs"
DOMAIN="homelab"

mkdir -p $CERT_DIR

echo "🔐 Installing local CA..."
mkcert -install

echo "📜 Generating wildcard cert..."
mkcert -cert-file $CERT_DIR/_wildcard.$DOMAIN.pem \
       -key-file $CERT_DIR/_wildcard.$DOMAIN-key.pem \
       "*.$DOMAIN"

echo "✅ Certificates generated in $CERT_DIR"