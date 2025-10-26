.PHONY: help build interactive
.DEFAULT_GOAL := help

IMAGE_NAME := closing-labels
GH_VERSION ?= 2.82.1

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

build: ## Build the docker image
	@echo "Building Docker image $(IMAGE_NAME) with GH version $(GH_VERSION)"
	docker build --build-arg GH_VERSION=$(GH_VERSION) -t $(IMAGE_NAME) .

interactive:  ## Interactive docker container
	docker run --rm -it --entrypoint bash -v $(shell pwd):/app -w /app -e GH_TOKEN=$(shell gh auth token) $(IMAGE_NAME)
