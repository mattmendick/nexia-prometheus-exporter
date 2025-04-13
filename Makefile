# Image name and tag
IMAGE_NAME := mattmendick/nexia-prometheus-exporter
VERSION := 0.0.1
PLATFORMS := linux/amd64,linux/arm64

.PHONY: build push clean login buildx-setup

# Setup buildx for multi-architecture builds
buildx-setup:
	docker buildx create --use --name multi-arch-builder || true

# Login to Docker Hub
login:
	docker login

# Build the Docker image for local architecture
build:
	docker build \
		--tag $(IMAGE_NAME):$(VERSION) \
		--tag $(IMAGE_NAME):latest \
		.

# Build and push multi-arch images to Docker Hub
push: login buildx-setup
	docker buildx build \
		--platform $(PLATFORMS) \
		--tag $(IMAGE_NAME):$(VERSION) \
		--tag $(IMAGE_NAME):latest \
		--push \
		.

# Clean up local Docker images and buildx builder
clean:
	docker rmi $(IMAGE_NAME):$(VERSION) $(IMAGE_NAME):latest || true
	docker buildx rm multi-arch-builder || true 