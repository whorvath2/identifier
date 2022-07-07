#!/bin/zsh

# Copyright © 2021 William L Horvath II
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

if ! [[ -a .env ]]
then
  echo ".env is missing"
  exit 1
fi

source .env

if [[ -a .dev_env ]]
then
  source .dev_env
fi

if ! { [[ -n $IDENTIFIER_DATA_PATH ]] \
&& [[ -n $IDENTIFIER_LOG_LEVEL ]] \
&& [[ -n $IDENTIFIER_MAX_READER_COUNT ]] \
&& [[ -n $IDENTIFIER_MAX_RETRIES ]] \
&& [[ -n $IDENTIFIER_TEXT_ENCODING ]] \
&& [[ -n $ROOT_LOG_LEVEL ]] \
&& [[ -n $FLASK_ENV ]] \
&& [[ -n $CERT_SUBJ ]] \
&& [[ -n $CERTS_DIR ]] \
&& [[ -n $TLS_DIR ]] \
&& [[ -n $CA_KEY_PATH ]] \
&& [[ -n $CA_BUNDLE_PATH ]] ; } \
then
  echo "All needed environment variables aren't specified: \
  IDENTIFIER_DATA_PATH: $IDENTIFIER_DATA_PATH \
  IDENTIFIER_LOG_LEVEL: $IDENTIFIER_LOG_LEVEL \
  IDENTIFIER_MAX_READER_COUNT: $IDENTIFIER_MAX_READER_COUNT \
  IDENTIFIER_MAX_RETRIES: $IDENTIFIER_MAX_RETRIES \
  IDENTIFIER_TEXT_ENCODING: $IDENTIFIER_TEXT_ENCODING \
  ROOT_LOG_LEVEL: $ROOT_LOG_LEVEL \
  FLASK_ENV: $FLASK_ENV \
  CERT_SUBJ: $CERT_SUBJ \
  CERTS_DIR: $CERTS_DIR \
  TLS_DIR: $TLS_DIR \
  CA_KEY_PATH: $CA_KEY_PATH \
  CA_BUNDLE_PATH: $CA_BUNDLE_PATH"
  exit 1
fi




if ! [[ -a "$CA_KEY_PATH" ]]
then
  echo "CA key is missing!"
  exit 2
fi

if ! [[ -a "$CA_BUNDLE_PATH" ]]
then
  echo "CA certificate is missing!"
  exit 2
fi

IDENTIFIER_KEY_PATH="$TLS_DIR/private/identifier-key.pem"
IDENTIFIER_CSR_PATH="$CERTS_DIR/identifier.csr"
#IDENTIFIER_CERT_PATH="$CERTS_DIR/identifier.pem"
IDENTIFIER_CERT_PATH="$TLS_DIR/certs/identifier-chain-bundle.cert.pem"

if ! [[ -a "$IDENTIFIER_CERT_PATH" ]]
then
  if [[ -a "$IDENTIFIER_KEY_PATH" ]]
  then
    rm "$IDENTIFIER_KEY_PATH"
  fi

  openssl genrsa -out "$IDENTIFIER_KEY_PATH" 4096
  if [[ $(echo $?) -ne 0 ]]
  then
    echo "Error generating identifier key!"
    exit 3
  else
    echo "Generated key at $IDENTIFIER_KEY_PATH"
  fi

  if [[ -a "$IDENTIFIER_CSR_PATH" ]]
  then
    rm "$IDENTIFIER_CSR_PATH"
  fi

  openssl req \
  -new \
  -key "$IDENTIFIER_KEY_PATH" \
  -out "$IDENTIFIER_CSR_PATH" \
  -subj "$CERT_SUBJ" \
  -passin "file:$TLS_DIR/apass.enc"

  if [[ $(echo $?) -ne 0 ]]
  then
    echo "Error creating certificate signing request!"
    rm "$IDENTIFIER_CSR_PATH"
    exit 3
  fi

  openssl ca \
  -batch \
  -cert "$CA_BUNDLE_PATH" \
  -config "$TLS_DIR/openssl.cnf" \
  -extfile "$CERTS_DIR/server_cert_ext.cnf" \
  -in "$IDENTIFIER_CSR_PATH" \
  -out "$IDENTIFIER_CERT_PATH" \
  -days 365 \
  -passin "file:$TLS_DIR/apass.enc" \
  -keyfile "$CA_KEY_PATH"
  if [[ $(echo $?) -ne 0 ]]
  then
    echo "Error creating server certificate!"
    rm "$IDENTIFIER_KEY_PATH"
    rm "$IDENTIFIER_CSR_PATH"
    rm "$IDENTIFIER_CERT_PATH"
    exit 3
  fi

  openssl x509 -in "$IDENTIFIER_CERT_PATH" -out "$IDENTIFIER_CERT_PATH" -outform PEM
  if [[ $(echo $?) -ne 0 ]]
  then
    echo "Error converting server certificate to PEM!"
    rm "$IDENTIFIER_KEY_PATH"
    rm "$IDENTIFIER_CSR_PATH"
    rm "$IDENTIFIER_CERT_PATH"
    exit 3
  fi
fi

if ! [[ -a "$IDENTIFIER_KEY_PATH" ]]
then
  echo "Identifier certificate key at $IDENTIFIER_KEY_PATH is missing!"
  exit 2
fi


echo "Removing secrets..."
podman secret rm identifier_cert_key
podman secret rm identifier_cert_pub
podman secret rm identifier_cert_ca_pub

echo "Creating secrets..."
podman secret create identifier_cert_key "$IDENTIFIER_KEY_PATH"
podman secret create identifier_cert_pub "$IDENTIFIER_CERT_PATH"
podman secret create identifier_cert_ca_pub "$CA_BUNDLE_PATH"

echo "Building the Identifier image..."
podman build \
--no-cache \
--secret id=identifier_cert_key,src="$IDENTIFIER_KEY_PATH" \
--secret id=identifier_cert_pub,src="$IDENTIFIER_CERT_PATH" \
--secret id=identifier_cert_ca_pub,src="$CA_BUNDLE_PATH" \
--env BUILD_ID="$BUILD_ID" \
--env ROOT_LOG_LEVEL="$ROOT_LOG_LEVEL" \
--env IDENTIFIER_LOG_LEVEL="$IDENTIFIER_LOG_LEVEL" \
--env IDENTIFIER_DATA_PATH="$IDENTIFIER_DATA_PATH" \
--env IDENTIFIER_MAX_READER_COUNT="$IDENTIFIER_MAX_READER_COUNT" \
--env IDENTIFIER_MAX_RETRIES="$IDENTIFIER_MAX_RETRIES" \
--env IDENTIFIER_TEXT_ENCODING="$IDENTIFIER_TEXT_ENCODING" \
--env FLASK_ENV="$FLASK_ENV" \
--env BUILD_ID="$BUILD_ID" \
--build-arg uuid=1001 \
--build-arg guid=1002 \
--build-arg identifier_data_path="$IDENTIFIER_DATA_PATH" \
--tag identifier_api_image \
--file Dockerfile

echo "Checking for identifier_api container..."
podman container ps -a | grep -s "identifier_api"
if [[ $(echo $?) -eq 0 ]]
then
  echo "Stopping and removing existing identifier_api container..."
  podman container stop identifier_api
  podman container rm identifier_api
fi

echo "Creating identifier_api container..."
podman create \
--replace \
--secret=identifier_cert_key,type=mount,target=/etc/ssl/private/identifier-key.pem,mode=0400 \
--secret=identifier_cert_pub,type=mount,target=/etc/ssl/certs/identifier.pem,mode=0444 \
--secret=identifier_cert_ca_pub,type=mount,target=/usr/local/share/ca-certificates/identifier_ca.pem,mode=0444 \
--name=identifier_api \
localhost/identifier_api_image:latest
