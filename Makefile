# Image name and tag
IMAGE_NAME := nexia-prometheus-exporter
VERSION := 0.0.1
GITHUB_USER := $(shell gh api user --jq .login)
DOCKER_REPO := ghcr.io/$(GITHUB_USER)
PLATFORMS := linux/amd64,linux/arm64

.PHONY: build push clean login buildx-setup

# Setup buildx for multi-architecture builds
buildx-setup:
	docker buildx create --use --name multi-arch-builder || true

# Login to GitHub Container Registry using gh cli
login:
	gh auth token | docker login ghcr.io -u $(GITHUB_USER) --password-stdin

# Build the Docker image for local architecture
build:
	docker build \
		--tag $(IMAGE_NAME):$(VERSION) \
		--tag $(IMAGE_NAME):latest \
		.

# Build and push multi-arch images to GitHub Container Registry
push: login buildx-setup
	docker buildx build \
		--platform $(PLATFORMS) \
		--tag $(DOCKER_REPO)/$(IMAGE_NAME):$(VERSION) \
		--tag $(DOCKER_REPO)/$(IMAGE_NAME):latest \
		--push \
		.

# Clean up local Docker images and buildx builder
clean:
	docker rmi $(IMAGE_NAME):$(VERSION) $(IMAGE_NAME):latest || true
	docker rmi $(DOCKER_REPO)/$(IMAGE_NAME):$(VERSION) $(DOCKER_REPO)/$(IMAGE_NAME):latest || true
	docker buildx rm multi-arch-builder || true 