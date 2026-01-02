.PHONY: help test test-unit test-integration test-e2e test-e2e-docker test-all test-frontend test-backend docker-up docker-down docker-logs docker-restart clean install install-backend install-frontend

# Default target
help:
	@echo "Schafkopf Game - Makefile Commands"
	@echo ""
	@echo "Testing Commands:"
	@echo "  make test              - Run all unit/integration tests (no Docker)"
	@echo "  make test-unit         - Run only unit tests"
	@echo "  make test-integration  - Run only integration tests"
	@echo "  make test-e2e          - Run E2E game logic tests (no Docker)"
	@echo "  make test-e2e-docker   - Run true E2E tests (requires Docker)"
	@echo "  make test-all          - Run all tests including Docker E2E"
	@echo "  make test-backend      - Run all backend tests (no Docker)"
	@echo "  make test-frontend     - Run frontend tests"
	@echo ""
	@echo "Docker Commands:"
	@echo "  make docker-up         - Start Docker containers"
	@echo "  make docker-down       - Stop Docker containers"
	@echo "  make docker-logs       - View Docker logs"
	@echo "  make docker-restart    - Restart Docker containers"
	@echo ""
	@echo "Setup Commands:"
	@echo "  make install           - Install all dependencies"
	@echo "  make install-backend   - Install backend dependencies"
	@echo "  make install-frontend  - Install frontend dependencies"
	@echo ""
	@echo "Utility Commands:"
	@echo "  make clean             - Clean up test artifacts and Docker volumes"

# ============================================================================
# Testing Commands
# ============================================================================

## Run all unit/integration tests (fast, no Docker)
test: test-backend
	@echo "✅ All tests completed (unit/integration only)"

## Run only unit tests
test-unit:
	@echo "🧪 Running unit tests..."
	cd backend && pytest tests/ -v -m unit

## Run only integration tests
test-integration:
	@echo "🔗 Running integration tests..."
	cd backend && pytest tests/ -v -m integration

## Run E2E game logic tests (no Docker)
test-e2e:
	@echo "🎮 Running E2E game logic tests..."
	cd backend && pytest tests/test_e2e_game_flow.py -v

## Run true E2E Docker tests (requires Docker)
test-e2e-docker: docker-up
	@echo "🐳 Waiting for Docker services to be ready..."
	@sleep 5
	@echo "🚀 Running E2E Docker tests..."
	cd backend && pytest tests/test_e2e_docker.py -v -m e2e_docker || (cd .. && make docker-down && exit 1)
	@$(MAKE) docker-down

## Run all tests including Docker E2E
test-all: test-backend docker-up
	@echo "🐳 Waiting for Docker services to be ready..."
	@sleep 5
	@echo "🚀 Running all tests including E2E Docker..."
	cd backend && pytest tests/ -v || (cd .. && make docker-down && exit 1)
	@$(MAKE) docker-down

## Run all backend tests (no Docker)
test-backend:
	@echo "🔧 Running backend tests (unit/integration/E2E game logic)..."
	cd backend && pytest tests/ -v -m "not e2e_docker"

## Run frontend tests
test-frontend:
	@echo "🎨 Running frontend tests..."
	cd frontend && npm test -- --run --reporter=verbose

## Run frontend tests in watch mode
test-frontend-watch:
	@echo "🎨 Running frontend tests in watch mode..."
	cd frontend && npm test

## Run frontend tests with UI
test-frontend-ui:
	@echo "🎨 Running frontend tests with UI..."
	cd frontend && npm run test:ui

# ============================================================================
# Docker Commands
# ============================================================================

## Start Docker containers
docker-up:
	@echo "🐳 Starting Docker containers..."
	docker-compose up -d
	@echo "⏳ Waiting for services to be ready..."
	@sleep 10
	@echo "✅ Docker containers started"

## Stop Docker containers
docker-down:
	@echo "🛑 Stopping Docker containers..."
	docker-compose down

## View Docker logs
docker-logs:
	@echo "📋 Viewing Docker logs (Ctrl+C to exit)..."
	docker-compose logs -f

## View backend logs only
docker-logs-backend:
	@echo "📋 Viewing backend logs (Ctrl+C to exit)..."
	docker-compose logs -f backend

## Restart Docker containers
docker-restart: docker-down docker-up
	@echo "🔄 Docker containers restarted"

## Check Docker container status
docker-status:
	@echo "📊 Docker container status:"
	docker-compose ps

# ============================================================================
# Setup Commands
# ============================================================================

## Install all dependencies
install: install-backend install-frontend
	@echo "✅ All dependencies installed"

## Install backend dependencies
install-backend:
	@echo "📦 Installing backend dependencies..."
	cd backend && pip install -r requirements.txt && pip install -r requirements-test.txt

## Install frontend dependencies
install-frontend:
	@echo "📦 Installing frontend dependencies..."
	cd frontend && npm install

# ============================================================================
# Coverage Commands
# ============================================================================

## Run backend tests with coverage
test-coverage:
	@echo "📊 Running tests with coverage..."
	cd backend && pytest tests/ -v -m "not e2e_docker" --cov=app --cov-report=html --cov-report=term
	@echo "📊 Coverage report generated in backend/htmlcov/index.html"

## Run backend tests with coverage (terminal only)
test-coverage-term:
	@echo "📊 Running tests with coverage (terminal)..."
	cd backend && pytest tests/ -v -m "not e2e_docker" --cov=app --cov-report=term

# ============================================================================
# Utility Commands
# ============================================================================

## Clean up test artifacts and Docker volumes
clean:
	@echo "🧹 Cleaning up..."
	@rm -rf backend/.pytest_cache
	@rm -rf backend/htmlcov
	@rm -rf backend/.coverage
	@rm -rf backend/test.db
	@rm -rf frontend/node_modules/.cache
	@rm -rf frontend/coverage
	@echo "✅ Cleanup complete"

## Clean Docker volumes (removes all data)
clean-docker:
	@echo "🧹 Cleaning Docker volumes (this will remove all data)..."
	docker-compose down -v
	@echo "✅ Docker volumes cleaned"

## Format code (if formatters are available)
format:
	@echo "🎨 Formatting code..."
	@if command -v black >/dev/null 2>&1; then \
		cd backend && black app/ tests/; \
	else \
		echo "⚠️  black not installed, skipping backend formatting"; \
	fi
	@if command -v prettier >/dev/null 2>&1; then \
		cd frontend && npx prettier --write "src/**/*.{ts,tsx,css}"; \
	else \
		echo "⚠️  prettier not installed, skipping frontend formatting"; \
	fi

## Lint code
lint:
	@echo "🔍 Linting code..."
	@if command -v flake8 >/dev/null 2>&1; then \
		cd backend && flake8 app/ tests/; \
	else \
		echo "⚠️  flake8 not installed, skipping backend linting"; \
	fi
	@cd frontend && npm run lint || echo "⚠️  Frontend linting failed or not configured"

# ============================================================================
# Development Commands
# ============================================================================

## Start development servers (Docker)
dev:
	@echo "🚀 Starting development environment..."
	docker-compose up

## Start development servers in background
dev-background:
	@echo "🚀 Starting development environment in background..."
	docker-compose up -d
	@echo "✅ Services running. Use 'make docker-logs' to view logs."

## Rebuild and start Docker containers
rebuild:
	@echo "🔨 Rebuilding Docker containers..."
	docker-compose up -d --build
	@echo "✅ Containers rebuilt and started"

# ============================================================================
# CI/CD Commands
# ============================================================================

## Run tests as they would in CI (no Docker E2E)
ci-test:
	@echo "🤖 Running CI test suite..."
	$(MAKE) test-backend
	$(MAKE) test-frontend

## Run full test suite including Docker E2E (for pre-deployment)
pre-deploy-test:
	@echo "🚀 Running pre-deployment test suite..."
	$(MAKE) test-all

