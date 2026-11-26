#!/usr/bin/env bash

# TODO:
#   echo version to be deployed.
#   some checks

docker compose -f docker-compose-prod.yml up --build --detach --remove-orphans

docker compose -f docker-compose-prod.yml restart backend