#!/usr/bin/env bash

# Prepare environment file and docker-compose
envsubst < ./docker/production/.env.dist > ./docker/production/.env
envsubst < ./docker/docker-compose.production.yml > ./docker/docker-compose.yml

# Prepare ssh connection with production server
eval $(ssh-agent -s)
echo "${DEPLOY_PRODUCTION_SSH_KEY}" | tr -d '\r' | ssh-add - > /dev/null
mkdir -p ~/.ssh
chmod 700 ~/.ssh

# Copy environment file and docker-compose to production server
scp -o 'StrictHostKeyChecking no' ./docker/production/.env ${SERVER_PRODUCTION}:/var/www/bicing-prediction-api/
scp -o 'StrictHostKeyChecking no' ./docker/docker-compose.yml ${SERVER_PRODUCTION}:/var/www/bicing-prediction-api/


# Run commands to update docker containers and run migrations
ssh -o "StrictHostKeyChecking no" ${SERVER_PRODUCTION} "docker login -u ${REGISTRY_PRODUCTION_LOGIN} -p ${REGISTRY_PRODUCTION_PASSOWRD} registry.gitlab.com"
ssh -o "StrictHostKeyChecking no" ${SERVER_PRODUCTION} "docker network create bicing-statistics-api-data || true"
ssh -o "StrictHostKeyChecking no" ${SERVER_PRODUCTION} "docker-compose -f /var/www/bicing-prediction-api/docker-compose.yml up -d"
ssh -o "StrictHostKeyChecking no" ${SERVER_PRODUCTION} "docker logout registry.gitlab.com"

# Clean
rm -rf ~/.ssh
rm ./docker/production/.env
rm ./docker/docker-compose.yml
