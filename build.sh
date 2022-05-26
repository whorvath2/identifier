#!/bin/zsh

source .env

# Check for the container and remove it if it's there already
if docker compose ls -a --filter name=identifier_api
then
  docker compose rm -s -v -f
fi

# Build the container and check it in to the repository as latest if it succeeds
if docker compose build
then
  docker commit identifier_api identifier_api
else
  echo "Unsuccessful build of the identifier_api container."
  exit 1
fi

# Start the container
docker compose up
