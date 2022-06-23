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
