#!/bin/zsh

source .env
source .env_dev

# Check for the container and remove it if it's there already
if docker compose ls -a --filter name=identifier_api
then
  docker compose rm -s -v -f
fi

if docker container ls -a --filter name=identifier_api
then
  docker container rm devmetrics_api
fi

# Build and start the container
docker compose up --build
