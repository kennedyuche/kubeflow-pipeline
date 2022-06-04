image_name := sparkdocai
image_tag := v3.1.1

push_name := docaispark
push_tag :=  V3.1.1
registry_name := docaiacr

# Build image and add a tag
build :
	echo "Building docker image..."
	docker build -t ${image_name}:${image_tag} .
	# sudo docker build -t ${image_name}:${image_tag} .

# List docker images
list :
	docker image ls
	# sudo docker image ls

# Run image in bash
run :
	echo "Running docker image..."
	# docker run -it ${image_name}:${image_tag}
	docker run -it ${image_name}:${image_tag} /bin/bash

login :
	echo "Logging into acr"
	az acr login --name ${registry_name}

tag :
	docker tag ${image_name}:${image_tag} ${registry_name}".azurecr.io/${image_name}:${image_tag}"

push :
	docker push ${registry_name}".azurecr.io/${image_name}:${image_tag}"

stop:
	echo "Stopping docker image..."
	sudo docker stop ${image_name}:${image_tag}

list acr :
	echo "Listing azure container registry repositories..."
	az acr repository list --name ${registry_name} --output table

get pods :
	echo "Listing all pods in spark-operator namespace..."
	kubectl get pods -n spark-operator

get app :
	echo "Watching spark application deployment..."
	kubectl get sparkapplications -n spark-operator --watch
