ENV_FILE ?= .env
COMPOSE_FILE ?= docker-compose.yml
PROJECT_NAME ?= myproject

# Docker Compose command
DC := docker compose --env-file $(ENV_FILE) -p $(PROJECT_NAME) -f $(COMPOSE_FILE)

# Build images
build:
	$(DC) build

# Start containers in detached mode
up:
	$(DC) up -d

# Start containers and view logs
up-logs:
	$(DC) up

# Stop and remove containers, networks, volumes, and images
down:
	$(DC) down

# View logs
logs:
	$(DC) logs -f

# Restart the stack
restart:
	$(MAKE) down
	$(MAKE) up

# Show status
ps:
	$(DC) ps

# Rebuild and restart
rebuild:
	$(DC) up -d --build --force-recreate --remove-orphans

# Execute command in a running container
exec:
	@read -p "Enter service name: " service; \
	 docker exec -it $$(docker compose -p $(PROJECT_NAME) ps -q $$service) sh

.PHONY: build up up-logs down logs restart ps rebuild exec
