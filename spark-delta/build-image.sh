#!/bin/sh
set -euo pipefail

function log {
  echo "$@"
  return 0
}

export ACR_NAME=docaiacr
export AZ_CLIENT_ID=XXXX      # Update with client ID
export AZ_CLIENT_SECRET=XXXX  # Update with client secret
export AZ_TENANT_ID=XXXX      # Update with tenant ID
export IMAGE_NAME=spark-delta
export IMAGE_TAG=v1

# Login to Azure Account
log '✅ Authenticating with Azure...'

az login --service-principal -u $AZ_CLIENT_ID -p $AZ_CLIENT_SECRET --tenant $AZ_TENANT_ID


# Login to Azure Container Registry
log '✅ Authenticating with Azure Container Registry...'
az acr login --name $ACR_NAME


# Docker build image
log '✅ Docker building $IMAGE_NAME image for $IMAGE_TAG version...'

docker build -t $IMAGE_NAME:$IMAGE_TAG .

# Docker tag image
log '✅ Tagging image for deployment to Azure...'

docker tag $IMAGE_NAME:$IMAGE_TAG $ACR_NAME.azurecr.io/$IMAGE_NAME:$IMAGE_TAG

# Docker push image to container registry
log '✅ Push image to $ACR_NAME container registry...'

docker push $ACR_NAME.azurecr.io/$IMAGE_NAME:$IMAGE_TAG