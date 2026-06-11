#!/bin/bash

CERT_DIR="/etc/traefik/certs"
DOMAIN="homelab.local"

mkdir -p $CERT_DIR

echo "🔐 Installing local CA..."
mkcert -install

echo "📜 Generating wildcard cert..."
mkcert -cert-file $CERT_DIR/_wildcard.$DOMAIN.pem \
       -key-file $CERT_DIR/_wildcard.$DOMAIN-key.pem \
       "*.$DOMAIN"

chown -R root:root /etc/traefik
chgrp -R traefik /etc/traefik/certs
chmod 755 /etc/traefik
chmod 755 /etc/traefik/certs
chmod 640 /etc/traefik/certs/*-key.pem
chmod 644 /etc/traefik/certs/*.pem

echo "✅ Certificates generated in $CERT_DIR"