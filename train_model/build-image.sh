#!/bin/sh
set -euo pipefail

function log {
  echo "$@"
  return 0
}

export DOCKER_USER_NAME=XXXX     # Update with docker username      
export DOCKER_PASSWORD=XXXX      # Update with docker password
export IMAGE_NAME=train-model
export IMAGE_TAG=v1


# Login to Docker Container Registry
log '✅ Authenticating with Azure Container Registry...'
az acr login --name $ACR_NAME
echo ${ DOCKER_PASSWORD } | docker login -u ${ DOCKER_USER_NAME } --password-stdin

# Docker build image
log '✅ Docker building $IMAGE_NAME image for $IMAGE_TAG version...'

docker build -t $IMAGE_NAME:$IMAGE_TAG .


# Docker push image to container registry
log '✅ Push image to Dockerhub account...'

docker push $DOCKER_USER_NAME/$IMAGE_NAME:$IMAGE_TAG