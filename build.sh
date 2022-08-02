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
echo "Sourcing environment variables..."
if [[ -a .env ]]
then
  source .env
fi
if [[ -a .dev_env ]]
then
  source .dev_env
fi

echo "Checking environment..."
if ! [[ -n $IDENTIFIER_DATA_PATH && -n $IDENTIFIER_LOG_LEVEL && -n $ROOT_LOG_LEVEL && -n $HOST_NAME ]] ;
then
  echo "Error: All required environment variables aren't specified:
  IDENTIFIER_DATA_PATH: $IDENTIFIER_DATA_PATH
  IDENTIFIER_LOG_LEVEL: $IDENTIFIER_LOG_LEVEL
  ROOT_LOG_LEVEL: $ROOT_LOG_LEVEL
  HOST_NAME: $HOST_NAME"
  return 1
fi

echo "Setting up $HOST_NAME certificate..."
. ./certs/create_cert.sh "$HOST_NAME" "localhost"
if ! [[ -n $HOST_CA_BUNDLE_PATH && -n $HOST_KEY_PATH && -n $HOST_CERT_PATH ]] ;
then
  echo "Error: HOST_CA_BUNDLE_PATH, HOST_KEY_PATH, or HOST_CERT_PATH was not set by certs/create_cert.sh"
  return 1
fi

echo "Building the Identifier image..."
podman build \
--secret id=identifier_cert_bundle_pub,src="$HOST_CA_BUNDLE_PATH" \
--env BUILD_ID="$BUILD_ID" \
--env ROOT_LOG_LEVEL="$ROOT_LOG_LEVEL" \
--env IDENTIFIER_LOG_LEVEL="$IDENTIFIER_LOG_LEVEL" \
--env IDENTIFIER_DATA_PATH="$IDENTIFIER_DATA_PATH" \
--env IDENTIFIER_MAX_READER_COUNT="$IDENTIFIER_MAX_READER_COUNT" \
--env IDENTIFIER_MAX_RETRIES="$IDENTIFIER_MAX_RETRIES" \
--env IDENTIFIER_TEXT_ENCODING="$IDENTIFIER_TEXT_ENCODING" \
--env FLASK_ENV="$FLASK_ENV" \
--build-arg uuid=1001 \
--build-arg guid=1002 \
--build-arg identifier_data_path="$IDENTIFIER_DATA_PATH" \
--tag identifier_api_image \
--file Dockerfile

echo "Checking for identifier_api container..."
if podman container ps -a | grep -s "identifier_api" ;
then
  echo "Stopping and removing existing identifier_api container..."
  podman container stop identifier_api
  podman container rm identifier_api
fi

echo "Creating identifier_api container..."
podman create \
--replace \
--name=identifier_api \
localhost/identifier_api_image:latest
