APP_NAME=ukw
IMAGE_NAME=lttl.dev/${APP_NAME}
IMAGE_TAG=0.1.0

## help: print this help message
.PHONY: help
help:
	@echo 'usage: make <target>'
	@echo
	@echo '  where <target> is one of the following:'
	@echo
	@sed -n 's/^##//p' ${MAKEFILE_LIST} | column -t -s ':' | sed -e 's/^/ /'

## build: build the docker image
.PHONY: build
build:
	@echo "Building docker image..."
	@docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .
	@echo "Docker image built successfully."

## run: run the docker image as a container
.PHONY: run
run:
	@docker run -d \
  		--restart unless-stopped \
  		-p 5000:5000 \
		--name ${APP_NAME} ${IMAGE_NAME}:${IMAGE_TAG}

## stop: stops and force-removes the container
.PHONY: stop
stop:
	@docker stop ${APP_NAME}
	@docker rm -f ${APP_NAME}