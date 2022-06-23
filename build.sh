#!/bin/zsh

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

if ! { [[ -n $FLASK_ENV ]] \
&& [[ -n $BUILD_ID ]] \
&& [[ -n $CERT_SUBJ ]] \
&& [[ -n $IDENTIFIER_DATA_PATH ]] \
&& [[ -n $ROOT_LOG_LEVEL ]] \
&& [[ -n $IDENTIFIER_LOG_LEVEL ]] \
&& [[ -n $IDENTIFIER_DATA_PATH ]] \
&& [[ -n $IDENTIFIER_MAX_READER_COUNT ]] \
&& [[ -n $IDENTIFIER_MAX_RETRIES ]] \
&& [[ -n $IDENTIFIER_TEXT_ENCODING ]] ; } \
then
  echo "All needed environment variables aren't specified: BUILD_ID, IDENTIFIER_DATA_PATH, ROOT_LOG_LEVEL, IDENTIFIER_LOG_LEVEL, IDENTIFIER_DATA_PATH, IDENTIFIER_MAX_READER_COUNT, IDENTIFIER_MAX_RETRIES, IDENTIFIER_TEXT_ENCODING"
  exit 3
fi

ca_dir="$(mkcert -CAROOT)"
ca_cert="$ca_dir/rootCA.pem"
ca_key=$(cat "$ca_dir/rootCA-key.pem")

openssl req -x509 -nodes -days 3650 -newkey rsa:2048 \
-CA $ca_cert \
-CAkey $ca_key \
-keyout ./identifier.key \
-out ./identifier.crt \
-subj "$CERT_SUBJ"

podman secret create identifier_cert_key ./identifier.key
podman secret create identifier_cert_pub ./identifier.crt
podman secret create identifier_cert_ca_pub "$ca_cert"

podman build \
--jobs=3 \
--secret identifier_cert_key,type=mount,target=/etc/ssl/private/identifier.key,mode=0440 \
--secret identifier_cert_pub,type=mount,target=/etc/ssl/certs/identifier.crt,mode=0444 \
--secret identifier_cert_ca_pub,type=mount,target=/usr/local/share/ca-certificates/identifier_ca.crt,mode=0444 \
--env BUILD_ID=$BUILD_ID \
--env ROOT_LOG_LEVEL=$ROOT_LOG_LEVEL \
--env IDENTIFIER_LOG_LEVEL=$IDENTIFIER_LOG_LEVEL \
--env IDENTIFIER_DATA_PATH=$IDENTIFIER_DATA_PATH \
--env IDENTIFIER_MAX_READER_COUNT=$IDENTIFIER_MAX_READER_COUNT \
--env IDENTIFIER_MAX_RETRIES=$IDENTIFIER_MAX_RETRIES \
--env IDENTIFIER_TEXT_ENCODING=$IDENTIFIER_TEXT_ENCODING \
--build-arg uuid=1001 \
--build-arg guid=1002 \
--build-arg identifier_data_path=$IDENTIFIER_DATA_PATH \
--build-arg flask_env=$FLASK_ENV \
--build-arg build_id=$BUILD_ID \
--tag identifier_api_image \
--file Dockerfile
