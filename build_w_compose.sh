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

# Check for the project and remove it if it's there already
if docker compose ls -a --filter name=identifier_api
then
  docker compose rm -s -v -f
fi

# Build the service and check the image into the local repository if it succeeds
if docker compose build
then
  docker commit identifier_api identifier_api
else
  echo "Unsuccessful build of the identifier_api container."
  exit 1
fi

# Check for the container and remove it if it's there already
if docker container ls -a --filter name=identifier_api
then
  docker container rm identifier_api
fi

# Create and start the container
docker compose up
