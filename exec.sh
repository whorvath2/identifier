#!/bin/zsh

podman container stop identifier_api
podman container rm -f identifier_api
podman run -d -t \
--name=identifier_api \
--secret identifier_cert_key,type=mount,target=/etc/ssl/private/identifier.key,mode=0440 \
--secret identifier_cert_pub,type=mount,target=/etc/ssl/certs/identifier.crt,mode=0444 \
--secret identifier_cert_ca_pub,type=mount,target=/usr/local/share/ca-certificates/identifier_ca.crt,mode=0444 \
localhost/identifier_api_image:latest
