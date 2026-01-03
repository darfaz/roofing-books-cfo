# Makefile for CrewCFO Docker operations
# Usage: make <target>

.PHONY: help build up down logs restart clean test

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

build: ## Build Docker images
	docker-compose build

up: ## Start all services (API + Dashboard)
	docker-compose up -d

up-db: ## Start all services including PostgreSQL
	docker-compose --profile db up -d

up-full: ## Start all services including PostgreSQL and pgAdmin
	docker-compose --profile db --profile tools up -d

down: ## Stop all services
	docker-compose down

down-volumes: ## Stop all services and remove volumes
	docker-compose down -v

logs: ## View logs from all services
	docker-compose logs -f

logs-api: ## View API logs
	docker-compose logs -f api

logs-dashboard: ## View dashboard logs
	docker-compose logs -f dashboard

restart: ## Restart all services
	docker-compose restart

restart-api: ## Restart API service
	docker-compose restart api

restart-dashboard: ## Restart dashboard service
	docker-compose restart dashboard

clean: ## Remove containers, networks, and volumes
	docker-compose down -v --rmi all

exec-api: ## Execute bash in API container
	docker-compose exec api bash

exec-dashboard: ## Execute bash in dashboard container
	docker-compose exec dashboard bash

test: ## Run tests in API container
	docker-compose exec api pytest tests/

build-prod: ## Build production image
	docker build -f Dockerfile.prod -t crewcfo-api:latest .

ps: ## Show running containers
	docker-compose ps








